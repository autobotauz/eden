# Re-import necessary libraries after code execution state reset
import matplotlib.pyplot as plt

# Parameters
base_gate_health = 100  # Assume gate has 100% health
damage_per_swing = 3    # 3% per swing with no debuff
swing_interval = 10     # seconds per swing

# Debuff percentages to evaluate
debuff_percentages = [0, 10, 15, 22, 33]

# Calculate time to take down the keep gate for each debuff
def time_to_take_gate(debuff_percent):
    effective_damage = damage_per_swing * (1 - debuff_percent / 100)
    swings_needed = base_gate_health / effective_damage
    return swings_needed * swing_interval

# Compute time for each debuff level
times = [time_to_take_gate(d) for d in debuff_percentages]

# Plotting
fig, ax = plt.subplots(figsize=(10, 6))
ax.plot(debuff_percentages, times, marker='o', color='crimson')
ax.set_title("Impact of Siege Debuff on Time to Destroy Keep Gate")
ax.set_xlabel("Siege Damage Debuff (%)")
ax.set_ylabel("Time to Destroy Gate (seconds)")
ax.grid(True)

# Annotate each point
for x, y in zip(debuff_percentages, times):
    ax.annotate(f"{int(y)}s", (x, y), textcoords="offset points", xytext=(0,5), ha='center')

plt.tight_layout()
plt.show()