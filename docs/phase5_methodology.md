# SENTRANET — Phase 5 Mathematical Methodology & Formulas

## 1. Risk Fusion Formulation

The instantaneous security risk score $R_t \in [0.0, 1.0]$ combines supervised attack likelihood with unsupervised unusualness:

$$\text{Classification Attack Score } S_{\text{attack}} = \max\left(0.0, 1.0 - P(\text{BENIGN})\right)$$

$$\text{Raw Fused Risk } \tilde{R}_t = \alpha \cdot S_{\text{attack}} + \beta \cdot A_t$$

$$\text{Fused Risk } R_t = \text{clip}\left(\tilde{R}_t, 0.0, 1.0\right)$$

- $\alpha = 0.60$ (Classification Weight)
- $\beta = 0.40$ (Anomaly Weight)
- $\alpha + \beta = 1.0$

### Risk State Categorization
- **`LOW`**: $0.00 \le R_t \le 0.24$
- **`GUARDED`**: $0.25 \le R_t \le 0.49$
- **`ELEVATED`**: $0.50 \le R_t \le 0.74$
- **`HIGH`**: $0.75 \le R_t \le 1.00$

---

## 2. Temporal Risk Derivatives

To evaluate whether risk is escalating over time, the system computes causal finite differences using actual wall-clock elapsed minutes $\Delta t = \frac{t_T - t_{T-1}}{60 \text{ sec}}$:

### 1. Risk Delta
$$\Delta R(T) = R(T) - R(T-1)$$

### 2. Risk Velocity (Rate of Change per Minute)
$$v(T) = \frac{R(T) - R(T-1)}{\Delta t}$$

### 3. Risk Acceleration (Rate of Velocity Change per Minute$^2$)
$$a(T) = \frac{v(T) - v(T-1)}{\Delta t}$$

---

## 3. Risk Trend Classification

Trends are classified using configurable engineering thresholds:
- **`RAPIDLY_RISING`**: $v(T) \ge 0.05/\text{min}$ AND $a(T) \ge 0.01/\text{min}^2$
- **`RISING`**: $v(T) \ge 0.02/\text{min}$
- **`FALLING`**: $v(T) \le -0.02/\text{min}$
- **`STABLE`**: Otherwise

---

## 4. Attack Emergence Criteria

An attack signature is marked as emerging (`is_emerging = true`) if and only if all following conditions are met:
1. **Temporal History:** $\ge 3$ consecutive windows available in the causal buffer.
2. **Positive Growth:** $v(T) > 0.0$ or $R(T) > R(T-1)$.
3. **Class Persistence:** Candidate attack class $C_{\text{attack}} \neq \text{BENIGN}$ has been consecutively predicted across $\ge 2$ windows.
4. **Elevation Check:** Current risk $R_t \ge 0.50$ (ELEVATED) or anomaly score $A_t \ge 0.40$.

---

## 5. Time-to-Impact (ETA) Estimation

When attack emergence is confirmed and velocity $v > 0.0$, the time required for risk to extrapolate to the critical impact threshold ($\tau_{\text{critical}} = 0.75$, the `HIGH` risk boundary) is computed:

$$\text{Minutes to Critical Impact } \Delta t_{\text{impact}} = \frac{\tau_{\text{critical}} - R_t}{v}$$

$$\text{ETA (Seconds)} = \max\left(30, \text{round}\left(\Delta t_{\text{impact}} \times 60.0\right)\right)$$

- **Saturation Bound:** If $R_t \ge \tau_{\text{critical}}$, the attack has already breached critical levels: $\text{ETA} = 0\text{s}$.
- **Absence Rule:** If risk velocity $v \le 0$ or emergence is not confirmed, $\text{forecast\_available} = \text{false}$ and $\text{ETA} = \text{null}$.

---

## 6. Heuristic Forecast Confidence

Forecast confidence combines classification strength, trajectory velocity, and anomaly elevation:

$$\text{Normalized Trend Strength } \nu = \text{clip}\left(\frac{v}{0.08}, 0.0, 1.0\right)$$

$$\text{Forecast Confidence } \mathcal{C} = \text{clip}\left(0.40 \cdot \text{Conf}_{\text{cls}} + 0.30 \cdot \nu + 0.30 \cdot A_t, 0.0, 1.0\right)$$
