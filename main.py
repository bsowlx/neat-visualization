import sys
import os
from ui.map_editor import main as run_map_editor_main
from training import main as run_training_main
from demo_run import DemoRunner

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

def run_map_editor():
    try:
        run_map_editor_main()
    except SystemExit:
        pass
    return True

def run_neat_training():
    track_path = os.path.join(ROOT_DIR, "assets", "track.png")
    pose_path = os.path.join(ROOT_DIR, "assets", "start_pose.json")
    
    if not os.path.exists(track_path) or not os.path.exists(pose_path):
        print("ERROR: Track or start position not found")
        return False
    
    try:
        run_training_main()
    except SystemExit:
        pass
    return True

def run_demo():
    if not os.path.exists("best_genome.pkl"):
        print("\n[!] No trained model found. Please run Training first.")
        input("Press Enter to continue...")
        return False
        
    try:
        DemoRunner().run()
    except SystemExit:
        pass
    return True

def main():
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print("="*50)
        print("   NEAT AUTONOMOUS RACING - DEMO DASHBOARD")
        print("="*50)
        print("1. Launch Map Editor (Create Track)")
        print("2. Start NEAT Training (Evolve AI)")
        print("3. Run Turing Test (Human vs AI)")
        print("4. Exit")
        print("="*50)
        
        choice = input("Select an option (1-4): ").strip()
        
        if choice == "1":
            run_map_editor()
        elif choice == "2":
            run_neat_training()
        elif choice == "3":
            run_demo()
        elif choice == "4":
            print("Exiting...")
            break
        else:
            print("Invalid option.")
            
    return 0


if __name__ == "__main__":
    sys.exit(main())
