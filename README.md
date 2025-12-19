# NEAT Autonomous Racing Visualization

A Python-based project that uses the **NEAT (NeuroEvolution of Augmenting Topologies)** algorithm to train AI agents to drive a car on a custom-drawn track. The project features a map editor, a real-time training visualizer, and a "Turing Test" mode where you can race against your best AI model.

## 🚀 Features

-   **Map Editor**: Draw your own race tracks and set the starting position for the cars.
-   **NEAT Training**: Watch the AI learn to drive from scratch. The visualization includes:
    -   Real-time neural network structure.
    -   Sensor rays showing what the car "sees".
    -   Fitness tracking and generation info.
-   **Turing Test Mode**: Race against the best trained AI model to see if you can beat it.
-   **Customizable**: Adjust NEAT parameters in `config/neat-car.cfg` to experiment with evolution settings.

## 🛠️ Installation

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/bsowlx/neat-visualization.git
    cd neat-visualization
    ```

2.  **Install dependencies**:
    Make sure you have Python installed, then run:
    ```bash
    pip install -r requirements.txt
    ```

## 🎮 Usage

Run the main dashboard to access all features:

```bash
python main.py
```

You will be presented with a menu:

1.  **Launch Map Editor (Create Track)**:
    -   **Left Click**: Draw road.
    -   **Right Click**: Erase.
    -   **Scroll**: Adjust brush size.
    -   **Proceed**: Save the track and place the starting car position.
    -   *Note: You must create a track before training.*
        
2.  **Start NEAT Training (Evolve AI)**:
    -   Starts the evolutionary process.
    -   Cars will evolve over generations to maximize their distance traveled without crashing.
    -   The best genome is automatically saved to `best_genome.pkl`.

3.  **Run Turing Test (Human vs AI)**:
    -   Race against the AI using the arrow keys.
    -   **Arrow Keys**: Control the player car.
    -   **R**: Reset the race.
    -   *Requires a trained `best_genome.pkl` file.*

## 📂 Project Structure

```
neat-visualization/
├── assets/                 # Stores track images, car sprites, and saved data
├── config/
│   └── neat-car.cfg        # NEAT algorithm configuration
├── core/
│   └── car.py              # Car physics and sensor logic
├── render/                 # Visualization helpers
├── ui/
│   ├── map_editor.py       # Track drawing interface
│   └── visualizer.py       # Neural network visualization
├── demo_run.py             # Human vs AI race logic
├── main.py                 # Main entry point
├── training.py             # NEAT training loop
└── requirements.txt        # Project dependencies
```

## ⚙️ Configuration

The behavior of the NEAT algorithm can be tweaked in `config/neat-car.cfg`. Key parameters include:
-   `pop_size`: Number of cars in each generation.
-   `fitness_threshold`: The fitness score required to stop training.
-   `num_inputs`: Number of sensors (default is 5 distance sensors + 1 speed input).
-   `num_outputs`: Control outputs (Left, Right, Up, Down).

## 🧠 How it Works

1.  **Sensors**: Each car casts rays in different directions to detect the distance to the track borders.
2.  **Neural Network**: These distances + speed are fed into a neural network (evolved by NEAT) which decides the steering and acceleration.
3.  **Evolution**: Cars that drive further get a higher fitness score. The best performing cars are selected to reproduce and mutate for the next generation.

## 📝 License

This project is open source. Feel free to modify and experiment!
