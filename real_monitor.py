import csv
import asyncio
from telethon import TelegramClient
from transformers import pipeline
from datetime import datetime
import os
from database import db
from bson import ObjectId
import re

class RealTelegramMonitor:
    def __init__(self):
        # Load HuggingFace NLP model
        try:
            self.classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")
            self.nlp_available = True
        except:
            self.classifier = None
            self.nlp_available = False
            print("⚠️ NLP model not available, using keyword-only detection")
        
        # Define categories for classification
        self.labels = ["drug sale", "normal", "spam", "other"]
        
        # Enhanced drug-related keywords database
        self.drug_keywords = [
            # Common drugs (exact matches)
            "mdma", "lsd", "mephedrone", "cocaine", "heroin", "cannabis", "marijuana", 
            "ganja", "charas", "hash", "hashish", "weed", "pot", "ecstasy", "molly",
            "meth", "crystal", "acid", "grass",
            
            # Indian slang
            "maal", "stuff", "quality stuff", "brown sugar", "white powder",
            
            # Sales terms
            "home delivery", "cash on delivery", "discreet packaging", "safe delivery",
            "bulk discount", "wholesale", "price list", "dm for price", "whatsapp for details",
            "serious buyers", "quality guarantee", "stealth shipping", "express delivery",
            
            # Drug-related phrases
            "party pills", "happiness pills", "magic mushrooms", "crystal meth",
            "on sale", "available", "stock", "supply", "dealer", "supplier",
            
            # Emojis
            "💊", "🌿", "💉", "🔥", "💰", "📦"
        ]

    async def analyze_real_channel(self, api_id, api_hash, channel_link, channel_id):
        """Analyze a real Telegram channel for drug-related content"""
        results = []
        
        try:
            # Create unique session name
            session_name = f"real_session_{channel_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            print(f"🔍 Connecting to Telegram with API ID: {api_id}")
            print(f"📱 Analyzing channel: {channel_link}")
            
            # Create client and connect
            client = TelegramClient(session_name, api_id, api_hash)
            await client.connect()
            
            # Check if we're authorized (for public channels, this might not be needed)
            if not await client.is_user_authorized():
                print("⚠️ Not authorized, but trying to access public channel...")
            
            try:
                # Get channel entity first
                channel_entity = await client.get_entity(channel_link)
                print(f"✅ Channel found: {channel_entity.title if hasattr(channel_entity, 'title') else 'Unknown'}")
                
                message_count = 0
                suspicious_count = 0
                
                # Iterate through messages
                async for message in client.iter_messages(channel_entity, limit=50):
                    text = message.text or ""
                    if text.strip():
                        message_count += 1
                        print(f"📨 Processing message {message_count}: {text[:50]}...")
                        
                        # Analyze message
                        analysis_result = await self.analyze_message_real(text)
                        
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
                        
                        # Print suspicious messages
                        if analysis_result["prediction"] == "drug sale":
                            suspicious_count += 1
                            print(f"🚨 DRUG SALE DETECTED: {text[:80]}... (confidence: {analysis_result['confidence']:.2f})")
                            print(f"   Keywords found: {', '.join(analysis_result['keyword_matches'])}")
                
                print(f"✅ Analysis complete: {message_count} messages processed, {suspicious_count} suspicious")
                
                # Update channel status
                db.update_channel_status(channel_id, "monitored", datetime.utcnow())
                
            except Exception as channel_error:
                print(f"❌ Channel access error: {channel_error}")
                raise channel_error
            
            finally:
                await client.disconnect()
                
        except Exception as e:
            print(f"❌ Error monitoring channel: {str(e)}")
            db.update_channel_status(channel_id, "error")
            # Don't create dummy data if real monitoring fails
            raise e
        
        return results

    async def analyze_message_real(self, text):
        """Analyze a real message for drug-related content"""
        # Keyword matching with exact detection
        text_lower = text.lower()
        keyword_matches = []
        
        for keyword in self.drug_keywords:
            # For single words, use word boundaries
            if len(keyword.split()) == 1:
                pattern = r'\b' + re.escape(keyword.lower()) + r'\b'
                if re.search(pattern, text_lower):
                    keyword_matches.append(keyword)
            else:
                # For phrases, direct substring match
                if keyword.lower() in text_lower:
                    keyword_matches.append(keyword)
        
        # NLP classification if available
        if self.nlp_available and self.classifier:
            try:
                nlp_result = self.classifier(text, candidate_labels=self.labels)
                nlp_prediction = nlp_result["labels"][0]
                nlp_confidence = nlp_result["scores"][0]
            except:
                nlp_prediction = "normal"
                nlp_confidence = 0.5
        else:
            nlp_prediction = "normal"
            nlp_confidence = 0.5
        
        # Combined analysis - prioritize keyword matches for real data
        if keyword_matches:
            # Strong keyword detection = high confidence drug sale
            drug_names = ["mdma", "lsd", "cocaine", "heroin", "ecstasy", "maal", "charas", "ganja", "meth"]
            has_drug_name = any(drug.lower() in text_lower for drug in drug_names)
            
            if has_drug_name:
                final_prediction = "drug sale"
                final_confidence = 0.9  # Very high confidence for drug names
            elif len(keyword_matches) >= 2:
                final_prediction = "drug sale"
                final_confidence = 0.8  # High confidence for multiple keywords
            else:
                final_prediction = "drug sale"
                final_confidence = 0.7  # Moderate confidence for single keyword
        else:
            # No keywords, use NLP if available
            if self.nlp_available and nlp_prediction == "drug sale":
                final_prediction = "drug sale"
                final_confidence = nlp_confidence
            else:
                final_prediction = "normal"
                final_confidence = max(nlp_confidence, 0.6)
        
        return {
            "prediction": final_prediction,
            "confidence": final_confidence,
            "keyword_matches": keyword_matches,
            "nlp_prediction": nlp_prediction,
            "nlp_confidence": nlp_confidence
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

# Initialize real monitor
real_monitor = RealTelegramMonitor()
