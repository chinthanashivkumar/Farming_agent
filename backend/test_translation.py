"""
Quick test — run this to verify translation works before starting the server.
Usage:  python test_translation.py
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

print("Testing deep_translator...")
try:
    from deep_translator import GoogleTranslator
    kn = GoogleTranslator(source='en', target='kn').translate(
        "Paddy needs 150mm water per week. Apply urea 50kg per acre."
    )
    hi = GoogleTranslator(source='en', target='hi').translate(
        "Paddy needs 150mm water per week. Apply urea 50kg per acre."
    )
    print(f"✅ Kannada: {kn}")
    print(f"✅ Hindi:   {hi}")
except Exception as e:
    print(f"❌ Translation failed: {e}")
    print("   Run:  python -m pip install deep_translator")
    sys.exit(1)

print("\nAll checks passed. Start the server with:  python main.py")
