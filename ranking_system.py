# Ranking System Constants

# Rank Names
RANKS = {
    'BEGINNER': 'Beginner',
    'POKEBALL': 'Pokeball',
    'GREATBALL': 'Greatball',
    'ULTRABALL': 'Ultraball',
    'MASTERBALL': 'Masterball'
}

# Points required for each rank
RANK_THRESHOLDS = {
    'BEGINNER_1': 0,
    'BEGINNER_2': 20,
    'BEGINNER_3': 50,
    'BEGINNER_4': 95,
    'POKEBALL_1': 145,
    'POKEBALL_2': 195,
    'POKEBALL_3': 245,
    'POKEBALL_4': 300,
    'GREATBALL_1': 355,
    'GREATBALL_2': 420,
    'GREATBALL_3': 490,
    'GREATBALL_4': 600,
    'ULTRABALL_1': 710,
    'ULTRABALL_2': 860,
    'ULTRABALL_3': 1010,
    'ULTRABALL_4': 1225,
    'MASTERBALL': 1450
}

# Points gained/lost per match
POINTS_WIN = 10
POINTS_LOSS = {
    'BEGINNER': 0,
    'POKEBALL': 5,
    'GREATBALL': 5,
    'ULTRABALL': 7,
    'MASTERBALL': 10
}

# Consecutive win bonus settings
CONSECUTIVE_WIN_BONUS = 3
MAX_CONSECUTIVE_WIN_BONUS = 12
MAX_CONSECUTIVE_WINS_FOR_BONUS = 4  # This will give max bonus of 12 (3 * 4)

# Rank progression
RANK_PROGRESSION = [
    'BEGINNER_1', 'BEGINNER_2', 'BEGINNER_3', 'BEGINNER_4',
    'POKEBALL_1', 'POKEBALL_2', 'POKEBALL_3', 'POKEBALL_4',
    'GREATBALL_1', 'GREATBALL_2', 'GREATBALL_3', 'GREATBALL_4',
    'ULTRABALL_1', 'ULTRABALL_2', 'ULTRABALL_3', 'ULTRABALL_4',
    'MASTERBALL'
]

# Simulation settings
import numpy as np
import matplotlib.pyplot as plt
import torch
import time

# Check for Metal support on macOS
if torch.backends.mps.is_available():
    device = torch.device("mps")
    print("Using Apple Metal acceleration")
elif torch.cuda.is_available():
    device = torch.device("cuda")
    print("Using NVIDIA CUDA acceleration")
else:
    device = torch.device("cpu")
    print("Using CPU (no GPU acceleration available)")

# Generate 100 match results (1 for win, 0 for loss)
np.random.seed(42)  # For reproducibility
match_results = np.random.binomial(1, 0.5, 100)  # 50% win probability

def calculate_rank_progression(match_results):
    """Calculate rank progression using GPU-accelerated operations."""
    # Convert match results to torch tensor if it's not already
    if isinstance(match_results, np.ndarray):
        match_results = torch.tensor(match_results, device=device)
    
    points = 0
    current_rank = 'BEGINNER_1'
    consecutive_wins = 0
    rank_history = []
    points_history = []
    
    # Convert match results to CPU for iteration
    match_results_cpu = match_results.cpu().numpy()
    
    for result in match_results_cpu:
        if result == 1:  # Win
            points += POINTS_WIN
            consecutive_wins += 1
            
            if current_rank in RANK_PROGRESSION[:12]:
                bonus = min(consecutive_wins * CONSECUTIVE_WIN_BONUS, MAX_CONSECUTIVE_WIN_BONUS)
                points += bonus
        else:  # Loss
            consecutive_wins = 0
            rank_category = current_rank.split('_')[0]
            points -= POINTS_LOSS[rank_category]
            points = max(0, points)
        
        for rank in reversed(RANK_PROGRESSION):
            if points >= RANK_THRESHOLDS[rank]:
                current_rank = rank
                break
        
        rank_history.append(current_rank)
        points_history.append(points)
    
    return {
        'final_points': points,
        'final_rank': current_rank,
        'wins': int(torch.sum(match_results).item()),
        'losses': len(match_results) - int(torch.sum(match_results).item()),
        'rank_history': rank_history,
        'points_history': points_history
    }

# Calculate results
results = calculate_rank_progression(match_results)

# Print text results
print(f"Final Points: {results['final_points']}")
print(f"Final Rank: {results['final_rank']}")
print(f"Total Wins: {results['wins']}")
print(f"Total Losses: {results['losses']}")
print("\nRank Progression:")
for i, (rank, points) in enumerate(zip(results['rank_history'], results['points_history'])):
    if i == 0 or rank != results['rank_history'][i-1]:
        print(f"Match {i+1}: {rank} (Points: {points})")

# Create visualization
plt.style.use('bmh')  # Using a built-in matplotlib style
fig, ax = plt.subplots(figsize=(15, 8))

# Plot points progression
matches = range(1, len(results['points_history']) + 1)
ax.plot(matches, results['points_history'], 'b-', label='Points', linewidth=2)

# Find rank change points
rank_changes = []
for i in range(1, len(results['rank_history'])):
    if results['rank_history'][i] != results['rank_history'][i-1]:
        rank_changes.append((i+1, results['points_history'][i], results['rank_history'][i]))

# Color regions for different ranks
colors = {
    'BEGINNER': '#FFB6C1',  # Light pink
    'POKEBALL': '#98FB98',  # Light green
    'GREATBALL': '#87CEEB',  # Sky blue
    'ULTRABALL': '#DDA0DD',  # Plum
    'MASTERBALL': '#F0E68C'   # Khaki
}

# Add colored regions and rank change markers
current_rank = results['rank_history'][0]
start_idx = 0
for i, rank in enumerate(results['rank_history']):
    if rank != current_rank or i == len(results['rank_history'])-1:
        rank_category = current_rank.split('_')[0]
        ax.axvspan(start_idx, i+1, alpha=0.2, color=colors[rank_category])
        current_rank = rank
        start_idx = i

# Add rank change markers and labels
for match_num, points, rank in rank_changes:
    ax.plot(match_num, points, 'ro', markersize=8)
    ax.annotate(f'Match {match_num}\n{rank}', 
                xy=(match_num, points),
                xytext=(10, 10),
                textcoords='offset points',
                bbox=dict(boxstyle='round,pad=0.5', fc='yellow', alpha=0.5),
                arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0'))

# Add rank threshold lines
for rank, threshold in RANK_THRESHOLDS.items():
    if threshold > 0:  # Skip BEGINNER_1 (0 points)
        ax.axhline(y=threshold, color='gray', linestyle='--', alpha=0.3)
        ax.text(len(matches), threshold, f' {rank}', verticalalignment='bottom')

# Customize the plot
ax.set_title('Points Progression with Rank Changes', fontsize=14, pad=20)
ax.set_xlabel('Match Number', fontsize=12)
ax.set_ylabel('Points', fontsize=12)
ax.grid(True, alpha=0.3)

# Add legend for rank colors
from matplotlib.patches import Patch
legend_elements = [Patch(facecolor=color, alpha=0.2, label=rank) 
                  for rank, color in colors.items()]
ax.legend(handles=legend_elements, loc='upper left', bbox_to_anchor=(1, 1))

plt.tight_layout()
plt.show()

def run_single_simulation(n_games, win_probability):
    """Run a single simulation using GPU-accelerated random number generation."""
    # Generate random numbers on GPU
    match_results = torch.bernoulli(torch.full((n_games,), win_probability, device=device))
    results = calculate_rank_progression(match_results)
    return results

def get_all_rank_transitions(rank_history):
    """Get the match numbers for all rank transitions."""
    transitions = {}
    current_rank = rank_history[0]
    
    # Initialize transitions for all ranks
    for i in range(len(RANK_PROGRESSION) - 1):
        from_rank = RANK_PROGRESSION[i]
        to_rank = RANK_PROGRESSION[i + 1]
        transition_key = f"{from_rank}_to_{to_rank}"
        transitions[transition_key] = None
    
    # Track transitions
    for i, rank in enumerate(rank_history):
        if rank != current_rank:
            transition_key = f"{current_rank}_to_{rank}"
            if transition_key in transitions and transitions[transition_key] is None:
                transitions[transition_key] = i + 1
            current_rank = rank
    
    return transitions

def run_batch_simulations(n_simulations, n_games, win_probability, batch_size=100):
    """Run multiple simulations in parallel batches using GPU."""
    # Initialize transition data for all possible rank transitions
    transition_data = {}
    for i in range(len(RANK_PROGRESSION) - 1):
        from_rank = RANK_PROGRESSION[i]
        to_rank = RANK_PROGRESSION[i + 1]
        transition_key = f"{from_rank}_to_{to_rank}"
        transition_data[transition_key] = []
    
    n_batches = (n_simulations + batch_size - 1) // batch_size
    
    for batch in range(n_batches):
        batch_size_actual = min(batch_size, n_simulations - batch * batch_size)
        match_results = torch.bernoulli(torch.full((batch_size_actual, n_games), win_probability, device=device))
        
        for i in range(batch_size_actual):
            results = calculate_rank_progression(match_results[i])
            transitions = get_all_rank_transitions(results['rank_history'])
            
            for key in transition_data:
                if transitions[key] is not None:
                    transition_data[key].append(transitions[key])
    
    return transition_data

def analyze_probabilities():
    """Analyze rank transitions across different win probabilities using GPU acceleration."""
    n_simulations = 1000
    n_games = 2000
    probabilities = np.arange(0.4, 0.8, 0.05)
    
    # Initialize results for all possible transitions
    results = {}
    for i in range(len(RANK_PROGRESSION) - 1):
        from_rank = RANK_PROGRESSION[i]
        to_rank = RANK_PROGRESSION[i + 1]
        transition_key = f"{from_rank}_to_{to_rank}"
        results[transition_key] = {
            'mean': [],
            'median': [],
            'raw_data': []  # Store raw data for frequency distribution
        }
    
    start_time = time.time()
    
    for prob in probabilities:
        print(f"\nAnalyzing win probability: {prob:.1f}")
        transition_data = run_batch_simulations(n_simulations, n_games, prob)
        
        for transition, data in transition_data.items():
            if data:
                # Store raw data
                results[transition]['raw_data'].extend(data)
                
                # Calculate statistics
                data_tensor = torch.tensor(data, dtype=torch.float32, device=device)
                results[transition]['mean'].append(torch.mean(data_tensor).item())
                results[transition]['median'].append(torch.median(data_tensor).item())
            else:
                results[transition]['mean'].append(np.nan)
                results[transition]['median'].append(np.nan)
                results[transition]['raw_data'].append(None)
    
    end_time = time.time()
    print(f"\nTotal analysis time: {end_time - start_time:.2f} seconds")
    
    return results, probabilities

def plot_probability_analysis(results, probabilities):
    """Plot mean and median games needed for each transition across probabilities."""
    # Move data to CPU for plotting
    for transition in results:
        results[transition]['mean'] = [x if isinstance(x, (int, float)) else x.item() 
                                     for x in results[transition]['mean']]
        results[transition]['median'] = [x if isinstance(x, (int, float)) else x.item() 
                                       for x in results[transition]['median']]
    
    # Create subplots based on rank categories
    rank_categories = ['BEGINNER', 'POKEBALL', 'GREATBALL', 'ULTRABALL', 'MASTERBALL']
    n_categories = len(rank_categories)
    
    fig, axes = plt.subplots(n_categories, 1, figsize=(15, 4*n_categories))
    fig.suptitle('Games Needed for Rank Transitions vs Win Probability', fontsize=16, y=0.95)
    
    # Group transitions by category
    category_transitions = {category: [] for category in rank_categories}
    for transition in results.keys():
        for category in rank_categories:
            if category in transition:
                category_transitions[category].append(transition)
    
    # Plot each category
    for idx, category in enumerate(rank_categories):
        ax = axes[idx]
        transitions = category_transitions[category]
        
        for transition in transitions:
            data = results[transition]
            label = transition.split('_to_')[1]  # Show only the target rank
            ax.plot(probabilities, data['mean'], '-', label=f'{label} (Mean)', marker='o')
            ax.plot(probabilities, data['median'], '--', label=f'{label} (Median)', marker='s')
        
        ax.set_title(f'{category} Rank Transitions')
        ax.set_xlabel('Win Probability')
        ax.set_ylabel('Number of Games')
        ax.grid(True, alpha=0.3)
        ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        ax.set_xticks(probabilities)
        ax.set_xticklabels([f'{p:.1f}' for p in probabilities])
    
    plt.tight_layout()
    plt.show()

def plot_frequency_distributions(results, probabilities):
    """Plot frequency distributions for each rank class."""
    rank_categories = ['BEGINNER', 'POKEBALL', 'GREATBALL', 'ULTRABALL', 'MASTERBALL']
    
    # Create a figure for each rank category
    for category in rank_categories:
        # Get all transitions for this category
        category_transitions = [t for t in results.keys() if category in t]
        if not category_transitions:
            continue
            
        # Create subplot grid
        n_transitions = len(category_transitions)
        n_cols = min(2, n_transitions)
        n_rows = (n_transitions + n_cols - 1) // n_cols
        
        fig, axes = plt.subplots(n_rows, n_cols, figsize=(15, 5*n_rows))
        fig.suptitle(f'{category} Rank Transitions - Frequency Distribution', fontsize=16, y=0.95)
        
        # Flatten axes for easier iteration
        if n_rows > 1:
            axes = axes.flatten()
        elif n_cols == 1:
            axes = [axes]
        
        # Plot each transition
        for idx, transition in enumerate(category_transitions):
            ax = axes[idx]
            data = results[transition]
            
            # Get all data points across probabilities
            all_games = []
            for prob_idx, prob in enumerate(probabilities):
                if not np.isnan(data['mean'][prob_idx]):
                    # Get the raw data for this probability
                    games_data = [d for d in data.get('raw_data', []) if d is not None]
                    all_games.extend(games_data)
            
            if all_games:
                # Create histogram
                ax.hist(all_games, bins=30, alpha=0.7, color='skyblue', edgecolor='black')
                
                # Add mean and median lines
                mean_games = np.mean(all_games)
                median_games = np.median(all_games)
                ax.axvline(mean_games, color='red', linestyle='--', 
                          label=f'Mean: {mean_games:.1f}')
                ax.axvline(median_games, color='green', linestyle='--', 
                          label=f'Median: {median_games:.1f}')
                
                # Customize plot
                ax.set_title(transition.replace('_', ' '))
                ax.set_xlabel('Number of Games')
                ax.set_ylabel('Frequency')
                ax.grid(True, alpha=0.3)
                ax.legend()
        
        # Hide unused subplots
        for idx in range(len(category_transitions), len(axes)):
            axes[idx].set_visible(False)
        
        plt.tight_layout()
        plt.show()

if __name__ == "__main__":
    # Run analysis and create visualization
    print("Starting probability analysis...")
    results, probabilities = analyze_probabilities()
    
    # Plot both probability analysis and frequency distributions
    plot_probability_analysis(results, probabilities)
    plot_frequency_distributions(results, probabilities)
    
    # Print detailed results
    print("\nDetailed Results:")
    for transition, data in results.items():
        print(f"\n{transition.replace('_', ' ')}:")
        print("Win Probability | Mean Games | Median Games")
        print("-" * 45)
        for i, prob in enumerate(probabilities):
            mean = data['mean'][i]
            median = data['median'][i]
            print(f"{prob:.1f}           | {mean:10.1f} | {median:11.1f}") 