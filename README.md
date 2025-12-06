# Mars Lander Heuristic – Short Description

This bot is a simple heuristic, which for each turn it checks the situation and chooses an angle and thrust that keep the ship safe

---

## Two flight phases

### **A) Traveling toward the flat zone**

When the ship is *not yet* above the landing zone:

* It moves left or right toward the center.
* If it is **far from the center** but **too low**, it climbs straight up at full power (avoids cliffs)
* If it is falling too fast near mountains, it also goes full power upward
* If horizontal speed is too low → tilt hard to accelerate
* If horizontal speed is too high → tilt opposite to brake
* If speeds are “okay” → keep angle near zero and control vertical speed

Goal:
**Reach the zone safely without crashing into anything**

---

### **B) Landing when above the flat zone**

Once horizontally above the landing area:

1. **Stop sliding sideways**
   If |hSpeed| is too big → tilt opposite your movement and use full power until nearly zero

2. **Fall vertically**
   Keep angle at 0°
   Adjust thrust:

   * falling too fast → full power
   * medium fall → medium power
   * gentle fall → no power

Goal:
**Land straight and slow**

---

## Edge Cases Covered

### **✔ Under-the-plateau danger**

If the ship is *not* above the flat zone **and** too close to the plateau height,
the bot forces **vertical full-power climb** so it doesn’t get trapped under cliffs

### **✔ Terrain height safety**

If the ship is close to the highest terrain and falling too fast,
it immediately switches to **full upward thrust**

### **✔ Too-low while far from center**

If the ship is far away horizontally but below a certain altitude margin,
it climbs before trying to move sideways

### **✔ Horizontal speed limits during landing**

If sliding too fast over the landing area,
the bot uses a braking tilt (~40°) with full thrust until safe

### **✔ Vertical landing speed limits**

As it gets close to the ground:

* It strictly limits vertical speed (aiming for better than the official −40 m/s requirement)

-----

## Result Evaluation and AI usage

Overall, the bot achieved a score of 2017 and placed in the top 10% of all participants, which is a strong result for a simple heuristic. To push the performance further, one could incorporate more advanced path-planning methods, such as a modified A–based approach or another optimized search strategy

I used AI to help implement the core ideas behind my heuristic: checking how close the lander is to the safe zone, detecting dangerous proximity to mountains, controlling horizontal speed toward the target, and stabilizing vertical speed for a safe descent. The AI turned these priorities into a working rule-based controller
