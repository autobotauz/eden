# Re-import necessary libraries after code execution state reset
import matplotlib.pyplot as plt

# Parameters
base_gate_health = 100  # Assume gate has 100% health
damage_per_swing = 3    # 3% per swing with no debuff
swing_interval = 10     # seconds per swing


# Buff percentages to evaluate (representing increased siege damage)
buff_percentages = [0, 10, 15]

# Calculate time to take down the keep gate for each buff
def time_with_buff(buff_percent):
    effective_damage = damage_per_swing * (1 + buff_percent / 100)
    swings_needed = base_gate_health / effective_damage
    return swings_needed * swing_interval

# Compute time for each buff level
buff_times = [time_with_buff(b) for b in buff_percentages]

# Plotting
fig, ax = plt.subplots(figsize=(10, 6))
ax.plot(buff_percentages, buff_times, marker='o', color='darkgreen')
ax.set_title("Impact of Siege Buff on Time to Destroy Keep Gate")
ax.set_xlabel("Siege Damage Buff (%)")
ax.set_ylabel("Time to Destroy Gate (seconds)")
ax.grid(True)

# Annotate each point
for x, y in zip(buff_percentages, buff_times):
    ax.annotate(f"{int(y)}s", (x, y), textcoords="offset points", xytext=(0,5), ha='center')

plt.tight_layout()
plt.show()
