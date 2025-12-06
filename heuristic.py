# ---------- Read surface and detect flat landing zone ----------
surface_n = int(input())
surface = []
for _ in range(surface_n):
    x, y = map(int, input().split())
    surface.append((x, y))

flat_x1 = flat_x2 = flat_y = None
max_terrain_y = 0

for i in range(1, surface_n):
    x1, y1 = surface[i - 1]
    x2, y2 = surface[i]
    max_terrain_y = max(max_terrain_y, y1, y2)

    # flat zone segment
    if y1 == y2:
        flat_x1, flat_x2, flat_y = x1, x2, y1

if flat_y is None:
    # should not happen, but keep things defined
    flat_x1, flat_x2, flat_y = 0, 0, 0

width = flat_x2 - flat_x1
flat_center_x = (flat_x1 + flat_x2) / 2.0

# --- define a narrower "safe band" inside the flat zone ---
# avoid edges: ~15% each side but at least 100m,
# never eat up more than 1/3 on each side.
if width > 0:
    edge_margin = min(width / 3.0, max(100.0, width * 0.15))
else:
    edge_margin = 0.0

edge_margin = 0.0

safe_x1 = flat_x1 + edge_margin
safe_x2 = flat_x2 - edge_margin
if safe_x2 <= safe_x1:
    # if the band collapses, just use full flat zone
    safe_x1, safe_x2 = flat_x1, flat_x2

safe_width = max(1.0, safe_x2 - safe_x1)

# ---------- Speed settings derived from safe zone width ----------
# Travel horizontal speed scales with how wide the safe band is:
# narrow safe zone → lower max horizontal speed for precision.

min_hs = 37
max_hs = 15 + safe_width ** 0.5 / 0.9
# print(15 + safe_width ** 0.5 / 0.9)

base_travel_hs = 15 + safe_width ** 0.5 / 1.0
TARGET_HSPEED_HIGH = min_hs          # far & high
TARGET_HSPEED_LOW = min_hs       # lower or closer
HSPEED_MARGIN = 6.0

# Max horizontal speed allowed while over the zone for landing
HS_LANDING_LIMIT = 18

# ---------- Vertical safety ----------
G = 3.711
SAFE_VSPEED = -35          # 35 m/s down
SAFE_VSPEED_APPROACH = -75 # softer while high
def SAFE_ALT_MARGIN(vSpeed):      # stay this much above highest terrain when travelling
    # return 0
    return vSpeed**2 / 1

# We also want not to drop below the flat plateau while far from the center
MIN_ALT_ABOVE_FLAT_WHEN_FAR = 465.0  # meters above flat when far from center

MAX_ANGLE_MOVE = 90        # tilt angle for moving horizontally

DANGER_ANGLE_BRAKE = 38
FAST_ANGLE_BRAKE = 42

MAX_ANGLE_BRAKE = 41       # tilt angle for braking horizontally


def sign(x):
    return 1 if x > 0 else (-1 if x < 0 else 0)


while True:
    try:
        X, Y, hSpeed, vSpeed, fuel, rotate, power = map(int, input().split())
    except EOFError:
        break

    angle_out = 0
    power_out = 0

    # ---------- EMERGENCY: we are under the flat / safe zone ----------
    # If we're horizontally inside the flat zone but below its altitude,
    # point straight up (angle 0) and full power until we're no longer under it.
    if not (flat_x1 <= X <= flat_x2) and Y < flat_y + SAFE_ALT_MARGIN(vSpeed):
        angle_out = 0
        power_out = 4

    else:
        # horizontal distance to center of landing zone
        dx = flat_center_x - X
        dist_x = abs(dx)

        # vertical distance above landing zone
        dy = Y - flat_y

        # are we over the *inner* safe band of the flat zone?
        over_safe_zone = safe_x1 <= X <= safe_x2

        # are we still "far" horizontally from the safe band center?
        far_from_center = dist_x > safe_width * 0.5

        # 1) If we are not over the inner band: travel / positioning phase
        if not over_safe_zone:
            direction = sign(dx)  # +1: need to go right, -1: need to go left

            # hard rule: when far from the center, do NOT go below the flat plateau
            if far_from_center and Y < flat_y + MIN_ALT_ABOVE_FLAT_WHEN_FAR:
                # climb / hold altitude
                angle_out = 0
                power_out = 4
            else:
                # choose target horizontal speed based on altitude
                if dy > 2000:
                    target_hs = TARGET_HSPEED_HIGH
                else:
                    target_hs = TARGET_HSPEED_LOW

                # "stay above mountains" rule
                if Y < max_terrain_y + SAFE_ALT_MARGIN(vSpeed) and vSpeed < SAFE_VSPEED_APPROACH:
                    # too low and falling fast -> point mostly up, full power
                    angle_out = 0
                    power_out = 4
                else:
                    # accelerate or brake horizontally
                    proj_speed = direction * hSpeed  # speed toward target side

                    if proj_speed < min_hs - HSPEED_MARGIN:
                        # need more horizontal speed toward target
                        # negative angle accelerates to the right, positive to the left
                        angle_out = -direction * MAX_ANGLE_MOVE
                        power_out = 4
                    elif proj_speed > max_hs + HSPEED_MARGIN:
                        # too fast, brake horizontally
                        if X-max_terrain_y < 500:
                            angle_out = direction * DANGER_ANGLE_BRAKE
                        else:
                            angle_out = direction * FAST_ANGLE_BRAKE
                        power_out = 4
                    else:
                        # horizontal speed within acceptable range
                        # keep mostly vertical, control vertical speed
                        angle_out = 0
                        if vSpeed < SAFE_VSPEED_APPROACH:
                            power_out = 4
                        elif vSpeed < -10:
                            power_out = 3
                        else:
                            power_out = 2

        # 2) Over inner safe band: braking + landing phase
        else:
            # first: limit horizontal speed according to safe width
            if abs(hSpeed) > HS_LANDING_LIMIT:
                # tilt opposite to horizontal speed
                direction = sign(hSpeed)  # +1 if moving right
                angle_out = direction * MAX_ANGLE_BRAKE  # positive -> accelerate left
                power_out = 4
            else:
                # kill angle and manage vertical speed
                angle_out = 0
                if vSpeed < SAFE_VSPEED - 0.2 * (dy)**0.5:
                    power_out = 4
                elif vSpeed < -27:
                    power_out = 3
                else:
                    power_out = 0

    # clamp outputs to allowed ranges
    if angle_out < -90:
        angle_out = -90
    elif angle_out > 90:
        angle_out = 90

    if power_out < 0:
        power_out = 0
    elif power_out > 4:
        power_out = 4

    print(f"{int(angle_out)} {int(power_out)}")
    # print(f"0 0")
