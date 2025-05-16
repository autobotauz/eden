import matplotlib.pyplot as plt

# Data from the table
relics_held = [0, 1, 2, 3, 4]
time_to_break_gate = [333, 407, 451, 470, 573]

# Plotting
fig, ax = plt.subplots(figsize=(10, 6))
ax.plot(relics_held, time_to_break_gate, marker='o', color='crimson')
ax.set_title("Dynamic Siege Modifier and Gate Health Based on Enemy Relics Held")
ax.set_xlabel("Number of Relics Held")
ax.set_ylabel("Time to Destroy Keep Gate (seconds)")
ax.set_xticks(relics_held)
ax.grid(True)

# Annotate each point
for x, y in zip(relics_held, time_to_break_gate):
    ax.annotate(f"{int(y)}s", (x, y), textcoords="offset points", xytext=(0,5), ha='center')

plt.tight_layout()
plt.show()
