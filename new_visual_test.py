import time
import os
from selenium import webdriver
from applitools.selenium import Eyes, Target, BatchInfo

# ---------------- CONFIG ----------------
APPLITOOLS_API_KEY = os.environ.get("APPLITOOLS_API_KEY", "YOUR_API_KEY")
batch = BatchInfo("Custom Responsive")

URLS_TO_TEST = [
    "https://b-there.in/",
    "https://b-there.in/sf/qr-generator"
]

VIEWPORTS = {
    "desktop": (1920, 1080),
    "laptop": (1366, 768), 
    "ipad_landscape": (1024, 768),
    "ipad_portrait": (768, 1024),
    "mobile_portrait_375": (375, 667),
    "mobile_portrait_425": (425, 667),
    "mobile_landscape": (812, 375),
}


def setup_driver_with_forced_scaling():
    """Setup driver with forced consistent scaling"""
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--force-device-scale-factor=1")
    options.add_argument("--disable-web-security")
    options.add_argument("--disable-features=VizDisplayCompositor")
    options.add_argument("--disable-gpu")  # Force consistent rendering
    return webdriver.Chrome(options=options)


def create_exact_baseline_then_compare(baseline_viewport, comparison_viewport, mapping_name):
   
    driver = setup_driver_with_forced_scaling()
    batch = BatchInfo(f"-{mapping_name}")

    try:
        print(f"\n🎯 MAPPING: {mapping_name}")
        print(f"📌 BASELINE: {baseline_viewport} {VIEWPORTS[baseline_viewport]}")
        print(f"🔍 COMPARISON: {comparison_viewport} {VIEWPORTS[comparison_viewport]}")

        for url_index, url in enumerate(URLS_TO_TEST):
            print(f"\n  🌐 Processing URL {url_index + 1}: {url}")

            # === PHASE 1: CREATE EXACT BASELINE ===
            print(f"  📌 PHASE 1: Creating EXACT baseline for {baseline_viewport}")

            baseline_width, baseline_height = VIEWPORTS[baseline_viewport]
            driver.set_window_size(baseline_width, baseline_height)
            driver.get(url)
            time.sleep(4)

            # Stabilize page
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1)
            driver.execute_script("window.scrollTo(0, 0);")
            time.sleep(2)

            # Create baseline with branch naming
            eyes_baseline = Eyes()
            eyes_baseline.api_key = APPLITOOLS_API_KEY
            eyes_baseline.batch = batch
            eyes_baseline.save_new_tests = True

            # Use branch to force specific baseline creation
            baseline_branch = f"BASELINE-{baseline_viewport}-{mapping_name}"
            eyes_baseline.branch_name = baseline_branch

            test_name = f"EXACT-{mapping_name}-URL{url_index + 1}"
            eyes_baseline.open(driver, " App", test_name,
                             {"width": baseline_width, "height": baseline_height})

            checkpoint_name = f"EXACT-BASELINE-{baseline_viewport}"
            eyes_baseline.check(checkpoint_name, Target.window().fully())
            baseline_result = eyes_baseline.close(False)
            print(f"    ✅ EXACT BASELINE CREATED: {baseline_branch}")

            # === PHASE 2: FORCE COMPARISON AGAINST EXACT BASELINE ===
            print(f"  🔍 PHASE 2: Forcing comparison for {comparison_viewport}")

            comparison_width, comparison_height = VIEWPORTS[comparison_viewport]
            driver.set_window_size(comparison_width, comparison_height)
            time.sleep(3)

            # Stabilize page at new size
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1)
            driver.execute_script("window.scrollTo(0, 0);")
            time.sleep(2)

            # Create comparison that references the exact baseline branch
            eyes_comparison = Eyes()
            eyes_comparison.api_key = APPLITOOLS_API_KEY
            eyes_comparison.batch = batch
            eyes_comparison.save_new_tests = False

            # KEY: Reference the baseline branch for comparison
            comparison_branch = f"COMPARE-{comparison_viewport}-vs-{baseline_viewport}"
            eyes_comparison.branch_name = comparison_branch
            eyes_comparison.parent_branch_name = baseline_branch  # Force baseline inheritance

            eyes_comparison.open(driver, "App", test_name,
                               {"width": comparison_width, "height": comparison_height})

            checkpoint_name = f"EXACT-COMPARE-{comparison_viewport}-vs-{baseline_viewport}"
            eyes_comparison.check(checkpoint_name, Target.window().fully())
            comparison_result = eyes_comparison.close(False)
            print(f"    ✅ EXACT COMPARISON COMPLETED: {comparison_branch}")

            print(f"    🔗 Baseline: {baseline_result}")
            print(f"    🔗 Comparison: {comparison_result}")

    except Exception as e:
        print(f"❌  COMPARISON FAILED: {e}")

    finally:
        driver.quit()


def perform_all_ultra_strict_mappings():

    mappings = [
        {
            "baseline": "desktop",
            "comparison": "laptop", 
            "name": "Desktop-to-Laptop-STRICT"
        },
        {
            "baseline": "laptop",
            "comparison": "ipad_landscape",
            "name": "Laptop-to-iPad-Landscape-STRICT"
        },
        {
            "baseline": "ipad_portrait",
            "comparison": "mobile_landscape", 
            "name": "iPad-Portrait-to-Mobile-Landscape-STRICT"
        },
        {
            "baseline": "mobile_portrait_375",
            "comparison": "mobile_portrait_425",
            "name": "Mobile-375-to-425-STRICT"
        }
    ]

    print("🚀 STARTING - CUSTOM BASELINE COMPARISON")
    print("=" * 70)
    print("This will create EXACT baseline-to-comparison mappings")
    print("Each mapping is completely isolated and enforced")

    for mapping_index, mapping in enumerate(mappings, 1):
        print(f"\n{'='*50}")
        print(f"EXECUTING MAPPING {mapping_index}/4: {mapping['name']}")
        print(f"{'='*50}")

        create_exact_baseline_then_compare(
            mapping["baseline"],
            mapping["comparison"], 
            mapping["name"]
        )

        print(f"✅ MAPPING {mapping_index} COMPLETED: {mapping['name']}")

    print("\n" + "="*70)
    print("🎯 ALL CUSTOM BASELINE MAPPINGS COMPLETED!")
    print("\n📊 EXPECTED DASHBOARD RESULTS:")
    print("• Each mapping appears as separate batch")
    print("• Baseline branches show established baselines")
    print("• Comparison branches show differences against exact baselines")
    print("• Branch names clearly indicate the baseline-to-comparison relationship")


if __name__ == "__main__":
    print("🎯 CUSTOM BASELINE COMPARISON")
    print("This FORCES your exact baseline-to-comparison mapping using:")
    print("• Branch-based baseline inheritance")
    print("• Isolated test execution per mapping")
    print("• Forced baseline creation and reference")
    print("• Complete override of Applitools default logic")

    confirm = input("\nExecute custom baseline comparison? (y/n): ")
    if confirm.lower() == 'y':
        perform_all_ultra_strict_mappings()
    else:
        print("❌ comparison cancelled.")
