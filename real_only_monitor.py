import csv
import asyncio
from telethon import TelegramClient
from telethon.errors import UsernameInvalidError, ChannelInvalidError
from transformers import pipeline
from datetime import datetime
import os
from database import db
from bson import ObjectId
import re

class RealOnlyTelegramMonitor:
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
        """Analyze a real Telegram channel - NO DEMO DATA FALLBACK"""
        results = []
        
        # Create unique session name
        session_name = f"real_only_{channel_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        print(f"🔍 Connecting to Telegram with NEW API credentials...")
        print(f"API ID: {api_id}")
        print(f"Channel: {channel_link}")
        
        client = None
        try:
            # Create client and connect
            client = TelegramClient(session_name, api_id, api_hash)
            await client.connect()
            print("✅ Connected to Telegram servers")
            
            # Check authorization status
            is_authorized = await client.is_user_authorized()
            print(f"Authorization status: {is_authorized}")
            
            # Extract channel identifier from link
            channel_identifier = channel_link.split('/')[-1]
            if channel_identifier.startswith('@'):
                channel_identifier = channel_identifier[1:]
            
            print(f"🔍 Trying to access channel: {channel_identifier}")
            
            # Try multiple methods to access the channel
            channel_entity = None
            methods = [
                # Method 1: Original link
                lambda: client.get_entity(channel_link),
                # Method 2: Username with @
                lambda: client.get_entity(f"@{channel_identifier}"),
                # Method 3: Just username
                lambda: client.get_entity(channel_identifier),
                # Method 4: Try with t.me format
                lambda: client.get_entity(f"t.me/{channel_identifier}"),
            ]
            
            for i, method in enumerate(methods, 1):
                try:
                    print(f"🔍 Attempting method {i}...")
                    channel_entity = await method()
                    print(f"✅ SUCCESS! Method {i} worked - Channel: {getattr(channel_entity, 'title', 'Unknown')}")
                    break
                except Exception as e:
                    print(f"⚠️ Method {i} failed: {type(e).__name__}: {e}")
                    continue
            
            if not channel_entity:
                error_msg = ("❌ FAILED: Could not access channel with any method. This may be due to:\n"
                           "1. Channel is private/restricted\n"
                           "2. API credentials lack channel access permissions\n"
                           "3. Channel doesn't exist or was deleted\n"
                           "4. Network/firewall issues")
                raise Exception(error_msg)
            
            # Successfully got channel - now fetch messages
            print(f"📨 Fetching messages from: {getattr(channel_entity, 'title', 'Unknown Channel')}")
            
            message_count = 0
            suspicious_count = 0
            
            # Get recent messages
            async for message in client.iter_messages(channel_entity, limit=50):
                if message.text and message.text.strip():
                    message_count += 1
                    text = message.text.strip()
                    
                    print(f"📝 Message {message_count}: {text[:60]}...")
                    
                    # Analyze message for drug content
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
                    
                    # Log suspicious messages
                    if analysis_result["prediction"] == "drug sale":
                        suspicious_count += 1
                        print(f"🚨 DRUG SALE DETECTED: {text[:100]}...")
                        print(f"   💯 Confidence: {analysis_result['confidence']:.2f}")
                        print(f"   🎯 Keywords: {', '.join(analysis_result['keyword_matches'])}")
                        print("---")
            
            print(f"✅ REAL DATA ANALYSIS COMPLETE!")
            print(f"📊 Total messages: {message_count}")
            print(f"🚨 Suspicious messages: {suspicious_count}")
            print(f"📈 Detection rate: {(suspicious_count/message_count*100) if message_count > 0 else 0:.1f}%")
            
            # Update channel status
            db.update_channel_status(channel_id, "monitored", datetime.utcnow())
            
        except Exception as e:
            print(f"❌ REAL MONITORING FAILED: {e}")
            # NO DEMO DATA FALLBACK - REAL DATA ONLY!
            db.update_channel_status(channel_id, "error")
            raise e  # Re-raise the error so user knows it failed
        
        finally:
            if client:
                await client.disconnect()
                print("🔌 Disconnected from Telegram")
        
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

# Initialize real-only monitor
real_only_monitor = RealOnlyTelegramMonitor()
