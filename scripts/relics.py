import matplotlib.pyplot as plt
import numpy as np

# Define the siege debuff logic for n relics
def get_siege_debuff(n):
    if n <= 0:
        return 0
    debuff = 10
    for _ in range(2, n + 1):
        debuff += debuff // 2
    return debuff

# Define the siege buff logic for m relics
def get_siege_buff(m):
    if m == 0:
        return 15
    elif m == 1:
        return 10
    else:
        return 0

# Generate values
n_values = list(range(0, 5))  # 0 to 5 relics held
debuffs = [get_siege_debuff(n) for n in n_values]
buffs = [get_siege_buff(m) for m in n_values]

# Create the plot
fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(n_values, debuffs, marker='o', label='Siege Damage Debuff (%) on Realm Holding Enemy Relics')
ax.plot(n_values, buffs, marker='s', label='Siege Damage Buff (%) on Realm Missing Relics')
ax.set_title("Dynamic Siege Modifier Based on Relics Held")
ax.set_xlabel("Number of Relics Held")
ax.set_ylabel("Modifier Percentage")
ax.legend()
ax.grid(True)
plt.xticks(n_values)
plt.tight_layout()

plt.show()
