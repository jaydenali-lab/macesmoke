package com.macesmoke;

import org.bukkit.Location;
import org.bukkit.Material;
import org.bukkit.Particle;
import org.bukkit.World;
import org.bukkit.entity.Entity;
import org.bukkit.entity.Player;
import org.bukkit.event.EventHandler;
import org.bukkit.event.EventPriority;
import org.bukkit.event.Listener;
import org.bukkit.event.entity.EntityDamageByEntityEvent;
import org.bukkit.inventory.ItemStack;
import org.bukkit.plugin.java.JavaPlugin;

/**
 * When a player lands a hit with a mace, an expanding circle of cloud-particle
 * smoke bursts out of the victim's body, flies outward fast, and lingers.
 */
public class MaceSmokePlugin extends JavaPlugin implements Listener {

    // How fast the smoke shoots outward from the body.
    private static final double OUTWARD_SPEED = 0.7;
    // Number of particles around each horizontal ring.
    private static final int POINTS_PER_RING = 28;
    // Vertical layers so smoke billows from the whole body, not a single line.
    private static final double[] RING_HEIGHTS = {-0.6, -0.2, 0.2, 0.6, 1.0};

    @Override
    public void onEnable() {
        getServer().getPluginManager().registerEvents(this, this);
        getLogger().info("MaceSmoke enabled. Mace hits now release a smoke circle.");
    }

    @EventHandler(priority = EventPriority.MONITOR, ignoreCancelled = true)
    public void onEntityDamage(EntityDamageByEntityEvent event) {
        if (!(event.getDamager() instanceof Player player)) {
            return;
        }

        ItemStack weapon = player.getInventory().getItemInMainHand();
        if (weapon.getType() != Material.MACE) {
            return;
        }

        Entity victim = event.getEntity();
        // Center the burst on the middle of the victim's body.
        Location center = victim.getLocation().add(0, victim.getHeight() / 2.0, 0);
        spawnSmokeCircle(center);
    }

    private void spawnSmokeCircle(Location center) {
        World world = center.getWorld();
        if (world == null) {
            return;
        }

        for (double dy : RING_HEIGHTS) {
            Location ringCenter = center.clone().add(0, dy, 0);
            for (int i = 0; i < POINTS_PER_RING; i++) {
                double angle = (2 * Math.PI / POINTS_PER_RING) * i;
                double dirX = Math.cos(angle);
                double dirZ = Math.sin(angle);
                // A slight vertical tilt by layer makes the cloud billow.
                double dirY = dy * 0.15;

                // count = 0 makes the offset arguments act as a velocity vector
                // and the final argument act as the speed multiplier, so each
                // cloud particle shoots outward from the body and then lingers.
                world.spawnParticle(
                        Particle.CLOUD,
                        ringCenter,
                        0,
                        dirX, dirY, dirZ,
                        OUTWARD_SPEED
                );
            }
        }
    }
}
