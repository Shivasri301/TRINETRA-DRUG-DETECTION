import csv
import asyncio
from telethon import TelegramClient
from datetime import datetime
import os
from database import db
from bson import ObjectId
from nlp_simple import SimpleNLPClassifier

class TelegramMonitor:
    def __init__(self):
        # Initialize lightweight NLP and keyword-based analysis
        print("🚀 Initializing lightweight NLP + keyword detection system")
        try:
            self.classifier = SimpleNLPClassifier()
            self.ai_available = True
            print("✅ Lightweight NLP initialized")
        except Exception as e:
            print(f"⚠️ NLP init failed: {e}. Falling back to keyword-only.")
            self.classifier = None
            self.ai_available = False
        
        # Define categories for classification
        self.labels = ["drug sale", "normal", "spam", "other"]
        
        # Enhanced drug-related keywords database with categories
        self.drug_keywords = {
            # High-confidence drug names
            "high_confidence": [
                "mdma", "lsd", "mephedrone", "cocaine", "heroin", "cannabis", "marijuana", 
                "ganja", "charas", "hash", "hashish", "weed", "pot", "ecstasy", "molly",
                "meth", "crystal meth", "acid", "brown sugar", "white powder"
            ],
            
            # Indian slang terms
            "indian_slang": [
                "maal", "stuff", "quality stuff", "party stuff", "green stuff",
                "supply", "stock", "product", "goods"
            ],
            
            # Sales and delivery terms
            "sales_terms": [
                "home delivery", "cash on delivery", "discreet packaging", "safe delivery",
                "quality guarantee", "bulk discount", "wholesale rates", "price list",
                "dm for price", "whatsapp for details", "serious buyers only",
                "stealth shipping", "express delivery", "doorstep delivery",
                "available", "in stock", "supply", "dealer", "supplier"
            ],
            
            # Drug-related emojis
            "emojis": ["💊", "🌿", "💉", "🔥", "⚡", "💯", "💰", "📦"]
        }
        
        # Flatten for backward compatibility
        self.all_keywords = []
        for category in self.drug_keywords.values():
            self.all_keywords.extend(category)

    async def analyze_channel(self, api_id, api_hash, channel_link, channel_id, phone_number=None):
        """Analyze a Telegram channel for drug-related content"""
        results = []
        
        try:
            # Try to use existing authenticated session first
            session_name = "authenticated_session"
            if not os.path.exists(f"{session_name}.session"):
                # Fallback to channel-specific session
                session_name = f"monitor_session_{channel_id}"
            
            client = TelegramClient(session_name, api_id, api_hash)
            await client.connect()
            
            # Check if client is authorized
            if not await client.is_user_authorized():
                await client.disconnect()
                raise Exception("Telegram session not authenticated. Please link your Telegram account first.")
            
            print(f"✅ Connected to Telegram for channel monitoring")
            
            try:
                async for message in client.iter_messages(channel_link, reverse=True, limit=100):
                    text = message.text or ""
                    if text.strip():
                        # Enhanced analysis combining NLP and keyword matching
                        analysis_result = await self.analyze_message(text)
                        
                        message_data = {
                            "message_id": message.id,
                            "sender_id": message.sender_id,
                            "date": message.date,
                            "message_text": text,
                            "prediction": analysis_result["prediction"],
                            "confidence": analysis_result["confidence"],
                            "keyword_matches": analysis_result["keyword_matches"]
                        }
                        
                        results.append(message_data)
                        
                        # Save to database
                        db.save_monitoring_result(channel_id, message_data)
                        
                        # Print suspicious messages for debugging
                        if analysis_result["prediction"] == "drug sale":
                            print(f"🚨 Drug-related message: {text[:80]}... (conf {analysis_result['confidence']:.2f})")
                
                # Update channel last monitored time
                db.update_channel_status(channel_id, "monitored", datetime.utcnow())
                print(f"✅ Successfully monitored {len(results)} messages")
                
            finally:
                # Always disconnect the client
                await client.disconnect()
                
        except Exception as e:
            print(f"Error monitoring channel: {str(e)}")
            db.update_channel_status(channel_id, "error")
            raise e
        
        return results

    async def analyze_message(self, text):
        """Analyze a single message for drug-related content with enhanced scoring"""
        text_lower = text.lower()
        keyword_matches = []
        confidence_boost = 0
        
        # Check keywords by category for weighted scoring
        for category, keywords in self.drug_keywords.items():
            category_matches = []
            for keyword in keywords:
                if keyword.lower() in text_lower:
                    category_matches.append(keyword)
                    keyword_matches.append(keyword)
            
            # Apply category-specific confidence boosts
            if category_matches:
                if category == "high_confidence":
                    confidence_boost += 0.3
                elif category == "indian_slang":
                    confidence_boost += 0.25
                elif category == "sales_terms":
                    confidence_boost += 0.15
                elif category == "emojis":
                    confidence_boost += 0.1
        
        # NLP classification (if available)
        if self.ai_available and self.classifier:
            try:
                nlp_result = self.classifier(text, candidate_labels=self.labels)
                nlp_prediction = nlp_result["labels"][0]
                nlp_confidence = nlp_result["scores"][0]
                # Build a mapping of label -> score for transparency
                nlp_label_scores = {label: score for label, score in zip(nlp_result["labels"], nlp_result["scores"]) }
            except Exception as e:
                print(f"NLP analysis failed: {e}, using keyword-only")
                nlp_prediction = "normal"
                nlp_confidence = 0.5
                nlp_label_scores = {label: (0.5 if label == "normal" else 0.0) for label in self.labels}
        else:
            # AI not available, use keyword-only analysis
            nlp_prediction = "normal"
            nlp_confidence = 0.5
            nlp_label_scores = {label: (0.5 if label == "normal" else 0.0) for label in self.labels}

        # Explicit drug-sale signal heuristics for gating
        price_or_currency = any(sym in text_lower for sym in ["$", "₹", "rs ", " price ", " rate ", " rs", " k "])
        contact_or_transaction = any(sig in text_lower for sig in [" dm ", "whatsapp", " telegram", " contact", " deal ", " order "])
        has_drug_terms = any(drug in text_lower for drug in self.drug_keywords["high_confidence"])
        has_drug_sale_signals = price_or_currency or contact_or_transaction or has_drug_terms

        # Enhanced combined analysis
        if keyword_matches:
            # Multiple categories = very high confidence
            categories_matched = sum(1 for cat, keywords in self.drug_keywords.items() 
                                   if any(k.lower() in text_lower for k in keywords))
            
            if categories_matched >= 2:
                final_prediction = "drug sale"
                final_confidence = min(0.95, nlp_confidence + confidence_boost)
            elif any(drug in text_lower for drug in self.drug_keywords["high_confidence"]):
                final_prediction = "drug sale"
                final_confidence = min(0.9, nlp_confidence + confidence_boost)
            else:
                final_prediction = "drug sale"
                final_confidence = min(0.8, max(nlp_confidence + confidence_boost, 0.6))
        else:
            # No keyword categories matched
            if has_drug_sale_signals:
                # Only then consider NLP output; otherwise default to normal
                final_prediction = nlp_prediction
                final_confidence = nlp_confidence
            else:
                # Force normal when there are no explicit drug-sale signals
                final_prediction = "normal"
                # Lower, variable confidence for clear normal to avoid many ~70% normals
                text_len = len(text_lower)
                if text_len < 30:
                    final_confidence = 0.30
                elif text_len < 120:
                    final_confidence = 0.40
                else:
                    final_confidence = 0.50
        
        return {
            "prediction": final_prediction,
            "confidence": final_confidence,
            "keyword_matches": keyword_matches,
            "nlp_prediction": nlp_prediction,
            "nlp_confidence": nlp_confidence,
            "nlp_label_scores": nlp_label_scores,
            "categories_matched": len(set(cat for cat, keywords in self.drug_keywords.items() 
                                        if any(k.lower() in text_lower for k in keywords)))
        }

    def export_results_to_csv(self, channel_id, filename=None):
        """Export monitoring results to CSV with enhanced formatting"""
        if not filename:
            filename = f"channel_{channel_id}_results.csv"
        
        # Get all results and sort by date (newest first)
        results = db.get_all_monitoring_results(channel_id) if hasattr(db, 'get_all_monitoring_results') else db.get_monitoring_results(channel_id, limit=1000)
        
        # Use UTF-8 with BOM for Excel compatibility on Windows
        with open(filename, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f)
            # Enhanced CSV header with more detailed information
            writer.writerow([
                "Message ID", "Sender ID", "Date & Time (UTC)", "Message Text", 
                "Prediction", "Confidence (%)", "Keyword Matches", "Categories Matched",
                "Message Length", "Processed At"
            ])
            
            for result in results:
                # Format date for better readability with comprehensive handling
                date_val = result.get("date")
                date_str = ""
                
                if date_val is not None:
                    try:
                        # Handle datetime objects
                        if hasattr(date_val, 'strftime'):
                            date_str = date_val.strftime('%Y-%m-%d %H:%M:%S UTC')
                        # Handle string dates
                        elif isinstance(date_val, str):
                            from datetime import datetime
                            try:
                                # Try parsing ISO format
                                parsed_date = datetime.fromisoformat(date_val.replace('Z', '+00:00'))
                                date_str = parsed_date.strftime('%Y-%m-%d %H:%M:%S UTC')
                            except:
                                date_str = date_val  # Use original string if parsing fails
                        # Handle timestamp numbers
                        elif isinstance(date_val, (int, float)):
                            from datetime import datetime
                            parsed_date = datetime.fromtimestamp(date_val)
                            date_str = parsed_date.strftime('%Y-%m-%d %H:%M:%S UTC')
                        else:
                            date_str = str(date_val)
                    except Exception as e:
                        print(f"⚠️ Date formatting error: {e}, using raw value")
                        date_str = str(date_val)
                else:
                    date_str = "No Date"
                
                # Clean message text (remove newlines that break CSV)
                message_text = result.get("message_text") or ""
                message_text = message_text.replace("\r\n", " ").replace("\n", " ").replace("\r", " ")
                
                # Format confidence as percentage
                confidence = result.get("confidence", 0)
                confidence_pct = f"{confidence * 100:.1f}" if isinstance(confidence, (int, float)) else str(confidence)
                
                # Get additional analysis data if available
                keyword_matches = result.get("keyword_matches", [])
                categories_matched = len(set(cat for cat, keywords in self.drug_keywords.items() 
                                           if any(k.lower() in message_text.lower() for k in keywords))) if keyword_matches else 0
                
                # Format processed_at date
                processed_at = result.get("processed_at")
                processed_str = ""
                if processed_at:
                    try:
                        if hasattr(processed_at, 'strftime'):
                            processed_str = processed_at.strftime('%Y-%m-%d %H:%M:%S UTC')
                        else:
                            processed_str = str(processed_at)
                    except:
                        processed_str = str(processed_at)
                else:
                    processed_str = "Unknown"
                
                # Calculate message length
                message_length = len(message_text) if message_text else 0
                
                writer.writerow([
                    result.get("message_id") or "N/A",
                    result.get("sender_id") or "N/A",
                    date_str,
                    message_text or "[No Text]",
                    result.get("prediction") or "unknown",
                    confidence_pct,
                    ", ".join(keyword_matches) if keyword_matches else "None",
                    categories_matched,
                    message_length,
                    processed_str
                ])
        
            # Add summary statistics at the end
            writer.writerow([])  # Empty row
            writer.writerow(["=== EXPORT SUMMARY ===", "", "", "", "", "", "", "", "", ""])
            
            # Calculate statistics
            total_messages = len(results)
            drug_sale_count = sum(1 for r in results if r.get("prediction") == "drug sale")
            normal_count = sum(1 for r in results if r.get("prediction") == "normal")
            spam_count = sum(1 for r in results if r.get("prediction") == "spam")
            other_count = sum(1 for r in results if r.get("prediction") == "other")
            
            avg_confidence = sum(float(r.get("confidence", 0)) for r in results) / total_messages if total_messages > 0 else 0
            
            # Export metadata
            from datetime import datetime
            export_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')
            
            writer.writerow(["Total Messages", total_messages, "", "", "", "", "", "", "", ""])
            writer.writerow(["Drug Sale Detected", drug_sale_count, f"({drug_sale_count/total_messages*100:.1f}%)", "", "", "", "", "", "", ""])
            writer.writerow(["Normal Messages", normal_count, f"({normal_count/total_messages*100:.1f}%)", "", "", "", "", "", "", ""])
            writer.writerow(["Spam Messages", spam_count, f"({spam_count/total_messages*100:.1f}%)", "", "", "", "", "", "", ""])
            writer.writerow(["Other Messages", other_count, f"({other_count/total_messages*100:.1f}%)", "", "", "", "", "", "", ""])
            writer.writerow(["Average Confidence", f"{avg_confidence*100:.1f}%", "", "", "", "", "", "", "", ""])
            writer.writerow(["Export Time", export_time, "", "", "", "", "", "", "", ""])
            writer.writerow(["Exported by", "Trinetra Drug Detection System", "", "", "", "", "", "", "", ""])
        
        print(f"✅ Exported {len(results)} results to {filename}")
        print(f"📊 Summary: {drug_sale_count} drug sales, {normal_count} normal, {spam_count} spam, {other_count} other")
        return filename

# Initialize monitor
monitor = TelegramMonitor()
