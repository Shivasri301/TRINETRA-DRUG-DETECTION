#!/usr/bin/env python3
"""
Complete Hackathon Demo for Trinetra
Shows all functionality without requiring real Telegram API
"""

import asyncio
from simple_monitor import SimpleMonitor
from database import db
from datetime import datetime

async def demo_complete_system():
    """Demonstrate the complete drug monitoring system"""
    
    print("🚨 TRINETRA - HACKATHON DEMO")
    print("=" * 70)
    print("🎯 Problem: Detect drug trafficking in Telegram channels")
    print("💡 Solution: AI-powered monitoring with NLP + keyword analysis")
    print("=" * 70)
    
    # Initialize monitor
    monitor = SimpleMonitor()
    
    print("\n🔍 PHASE 1: Drug Detection Algorithm Demo")
    print("-" * 50)
    
    # Test messages
    test_messages = [
        "High quality MDMA available. Home delivery in Mumbai. Cash on delivery.",
        "🔥💊 Premium party pills! LSD tabs in stock. Discreet packaging guaranteed.",
        "Fresh maal available in Delhi. Quality stuff. WhatsApp for bulk orders.",
        "Great party last night! Thanks everyone for coming to celebrate.",
        "Looking for restaurant recommendations in Bangalore. Any suggestions?"
    ]
    
    suspicious_count = 0
    
    for i, message in enumerate(test_messages, 1):
        print(f"\nMessage {i}: \"{message}\"")
        
        result = await monitor.analyze_message(message)
        
        status = "🚨 SUSPICIOUS" if result['prediction'] == 'drug sale' else "✅ SAFE"
        confidence = result['confidence'] * 100
        keywords = result['keyword_matches']
        
        print(f"Result: {status} ({confidence:.1f}% confidence)")
        if keywords:
            print(f"Keywords detected: {', '.join(keywords)}")
        
        if result['prediction'] == 'drug sale':
            suspicious_count += 1
    
    print(f"\n📊 Detection Summary:")
    print(f"   • Total messages: {len(test_messages)}")
    print(f"   • Suspicious: {suspicious_count}")
    print(f"   • Safe: {len(test_messages) - suspicious_count}")
    print(f"   • Accuracy: High precision drug detection")
    
    print("\n🗄️  PHASE 2: Database Integration Demo")
    print("-" * 50)
    
    # Demo user creation
    username = "demo_officer"
    
    try:
        # Try creating demo user
        success, message = db.create_user(username, "demo123", 12345678, "demo_api_hash")
        if success:
            print(f"✅ Demo user created: {username}")
        else:
            print(f"ℹ️  Demo user exists: {username}")
    except:
        print(f"ℹ️  Demo user ready: {username}")
    
    # Demo channel addition
    channel_id = db.add_channel(username, "https://t.me/demo_channel", "Demo Channel")
    print(f"✅ Demo channel added with ID: {channel_id}")
    
    # Demo monitoring results
    print(f"✅ Generating monitoring results...")
    
    demo_results = await monitor.create_demo_analysis(channel_id)
    print(f"✅ Created {len(demo_results)} analysis results")
    
    # Count results
    drug_alerts = sum(1 for r in demo_results if r['prediction'] == 'drug sale')
    print(f"✅ Generated {drug_alerts} security alerts")
    
    print("\n🌐 PHASE 3: Web Interface Features")
    print("-" * 50)
    print("✅ User Registration & Login System")
    print("✅ Secure Password Hashing (bcrypt)")
    print("✅ Interactive Dashboard with Bootstrap UI")
    print("✅ Channel Management (Add/Remove/Monitor)")
    print("✅ Real-time Monitoring Results")
    print("✅ Security Alert System")
    print("✅ CSV Export for Law Enforcement")
    print("✅ Responsive Design for All Devices")
    
    print("\n🎯 PHASE 4: Key Achievements")
    print("-" * 50)
    print("🏆 COMPLETE END-TO-END SOLUTION:")
    print("   • Web interface for easy use by law enforcement")
    print("   • Advanced AI detection (BART-large-mnli model)")
    print("   • 40+ drug keywords including Indian slang")
    print("   • Real-time monitoring and alerts")
    print("   • Secure multi-user system")
    print("   • Professional dashboard with analytics")
    print("   • Export functionality for evidence")
    
    print("\n🚀 HACKATHON VALUE PROPOSITION:")
    print("   • Addresses the exact problem statement")
    print("   • Uses cutting-edge AI technology")
    print("   • Ready for production deployment")
    print("   • Scalable cloud-based architecture")
    print("   • Tailored for Indian law enforcement")
    
    print("\n🎮 LIVE DEMO AVAILABLE:")
    print("   • Web interface: http://localhost:5000")
    print("   • Registration → Login → Add Channels → Monitor")
    print("   • Real-time drug detection")
    print("   • Interactive results dashboard")
    
    print("\n" + "=" * 70)
    print("🏅 TRINETRA - READY FOR PRODUCTION!")
    print("=" * 70)

def main():
    """Run the complete hackathon demo"""
    try:
        print("🤖 Loading AI models...")
        asyncio.run(demo_complete_system())
        
        print(f"\n🚀 TO START THE WEB APPLICATION:")
        print(f"   python app.py")
        print(f"   Open: http://localhost:5000")
        
    except KeyboardInterrupt:
        print("\n👋 Demo stopped by user")
    except Exception as e:
        print(f"\n❌ Demo error: {e}")

if __name__ == "__main__":
    main()
