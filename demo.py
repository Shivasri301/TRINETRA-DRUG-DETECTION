#!/usr/bin/env python3
"""
Demo script for testing the drug detection algorithm
This script demonstrates the NLP and keyword detection capabilities
"""

import asyncio
from telegram_monitor import TelegramMonitor

# Sample messages for testing
test_messages = [
    # Suspicious messages
    "High quality MDMA available. Home delivery in Mumbai. Cash on delivery. DM for price list.",
    "Party pills in stock! Best quality LSD tabs. Discreet packaging guaranteed. Contact for wholesale rates.",
    "Fresh maal available. Quality stuff. Free delivery in Delhi NCR. WhatsApp for details.",
    "🔥💊 Premium Ecstasy tablets 💊🔥 Safe delivery. Bulk discounts available. Serious buyers only.",
    
    # Normal messages
    "Great party last night! Thanks everyone for coming.",
    "Check out this new restaurant in Bangalore. Amazing food!",
    "Looking for a good gym in the area. Any recommendations?",
    "Happy birthday! Hope you have a wonderful day.",
    
    # Borderline messages
    "Feeling stressed? Try our natural relaxation products.",
    "Party supplies available. Contact for more information.",
    "Special delivery service in your area. Very discreet.",
    "Quality products at competitive prices. Limited time offer."
]

async def demo_analysis():
    """Demonstrate the drug detection algorithm"""
    print("🧪 Trinetra - Detection Demo")
    print("=" * 60)
    
    monitor = TelegramMonitor()
    
    print(f"🔍 Testing {len(test_messages)} sample messages...\n")
    
    suspicious_count = 0
    
    for i, message in enumerate(test_messages, 1):
        print(f"Message {i}:")
        print(f"Text: \"{message}\"")
        
        # Analyze message
        result = await monitor.analyze_message(message)
        
        prediction = result['prediction']
        confidence = result['confidence']
        keywords = result['keyword_matches']
        
        # Display results
        status_emoji = "🚨" if prediction == "drug sale" else "✅" if prediction == "normal" else "⚠️"
        print(f"Result: {status_emoji} {prediction.upper()} ({confidence:.1%} confidence)")
        
        if keywords:
            print(f"Keywords: {', '.join(keywords)}")
        
        if prediction == "drug sale":
            suspicious_count += 1
        
        print("-" * 60)
    
    # Summary
    print(f"\n📊 ANALYSIS SUMMARY:")
    print(f"Total Messages: {len(test_messages)}")
    print(f"Suspicious (Drug Sale): {suspicious_count}")
    print(f"Safe Messages: {len(test_messages) - suspicious_count}")
    print(f"Detection Rate: {suspicious_count/len(test_messages):.1%}")
    
    print("\n✅ Demo completed!")
    print("💡 Ready to monitor real Telegram channels!")

def main():
    """Run the demo"""
    try:
        # Check if transformers is available
        from transformers import pipeline
        print("🤖 Loading NLP model (this may take a moment on first run)...")
        
        # Run async demo
        asyncio.run(demo_analysis())
        
    except ImportError:
        print("❌ Missing dependencies. Run 'python setup.py' first.")
        import sys
        sys.exit(1)
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import sys
        sys.exit(1)

if __name__ == "__main__":
    main()
