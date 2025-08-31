import csv
import asyncio
from telethon import TelegramClient
from datetime import datetime
import os
from database import db
from bson import ObjectId

class TelegramMonitor:
    def __init__(self):
        # Use reliable keyword-based analysis only
        print("🚀 Initializing keyword-based drug detection system")
        self.classifier = None
        self.ai_available = False
        print("✅ Keyword-based detection system ready")
        
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
            except Exception as e:
                print(f"NLP analysis failed: {e}, using keyword-only")
                nlp_prediction = "normal"
                nlp_confidence = 0.5
        else:
            # AI not available, use keyword-only analysis
            nlp_prediction = "normal"
            nlp_confidence = 0.5
        
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
            # No keywords, rely on NLP
            final_prediction = nlp_prediction
            final_confidence = nlp_confidence
        
        return {
            "prediction": final_prediction,
            "confidence": final_confidence,
            "keyword_matches": keyword_matches,
            "nlp_prediction": nlp_prediction,
            "nlp_confidence": nlp_confidence,
            "categories_matched": len(set(cat for cat, keywords in self.drug_keywords.items() 
                                        if any(k.lower() in text_lower for k in keywords)))
        }

    def export_results_to_csv(self, channel_id, filename=None):
        """Export monitoring results to CSV"""
        if not filename:
            filename = f"channel_{channel_id}_results.csv"
        
        results = db.get_monitoring_results(channel_id)
        
        with open(filename, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                "Message ID", "Sender ID", "Date", "Message Text", 
                "Prediction", "Confidence", "Keyword Matches"
            ])
            
            for result in results:
                writer.writerow([
                    result.get("message_id"),
                    result.get("sender_id"),
                    result.get("date"),
                    result.get("message_text"),
                    result.get("prediction"),
                    result.get("confidence"),
                    ", ".join(result.get("keyword_matches", []))
                ])
        
        return filename

# Initialize monitor
monitor = TelegramMonitor()
