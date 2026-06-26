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
import org.bukkit.scheduler.BukkitRunnable;

/**
 * When a player lands a hit with a mace, a single packed ring of cloud-particle
 * smoke launches out of the victim's body and rises up to a max of 5 blocks.
 */
public class MaceSmokePlugin extends JavaPlugin implements Listener {

    // Maximum height the smoke ring rises, in blocks.
    private static final double MAX_HEIGHT = 5.0;
    // How many blocks the ring climbs per tick (controls launch speed).
    private static final double RISE_PER_TICK = 0.5;
    // Particles around the ring. Higher = more packed.
    private static final int POINTS_PER_RING = 64;
    // Starting radius of the ring at the body.
    private static final double START_RADIUS = 0.5;
    // How much the ring widens for every block it rises.
    private static final double RADIUS_GROWTH = 0.25;

    @Override
    public void onEnable() {
        getServer().getPluginManager().registerEvents(this, this);
        getLogger().info("MaceSmoke enabled. Mace hits now release a rising smoke circle.");
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

        // Launch from the victim's feet so the ring rises up through the body.
        spawnRisingSmokeRing(event.getEntity().getLocation());
    }

    private void spawnRisingSmokeRing(Location base) {
        World world = base.getWorld();
        if (world == null) {
            return;
        }

        new BukkitRunnable() {
            double height = 0.0;

            @Override
            public void run() {
                if (height > MAX_HEIGHT) {
                    cancel();
                    return;
                }

                double radius = START_RADIUS + height * RADIUS_GROWTH;
                Location ringCenter = base.clone().add(0, height, 0);

                for (int i = 0; i < POINTS_PER_RING; i++) {
                    double angle = (2 * Math.PI / POINTS_PER_RING) * i;
                    double x = Math.cos(angle) * radius;
                    double z = Math.sin(angle) * radius;
                    Location point = ringCenter.clone().add(x, 0, z);

                    // count > 0 with zero speed places packed particles that
                    // linger where they spawn instead of flying off.
                    world.spawnParticle(Particle.CLOUD, point, 2, 0.05, 0.05, 0.05, 0.0);
                }

                height += RISE_PER_TICK;
            }
        }.runTaskTimer(this, 0L, 1L);
    }
}
