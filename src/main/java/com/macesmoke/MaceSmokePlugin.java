package com.macesmoke;

import org.bukkit.Location;
import org.bukkit.Material;
import org.bukkit.Particle;
import org.bukkit.Sound;
import org.bukkit.SoundCategory;
import org.bukkit.World;
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
 * smoke bursts from the victim's torso and pans straight outward (no rising),
 * accompanied by heavy impact sounds.
 */
public class MaceSmokePlugin extends JavaPlugin implements Listener {

    // How far out the ring expands, in blocks.
    private static final double MAX_RADIUS = 5.0;
    // Starting radius at the torso.
    private static final double START_RADIUS = 0.4;
    // How many blocks the ring expands per tick (controls launch speed).
    private static final double EXPAND_PER_TICK = 0.45;
    // Particles around the ring. Higher = more packed.
    private static final int POINTS_PER_RING = 64;
    // Fraction of the victim's height to use as the torso point (~chest level).
    private static final double TORSO_FRACTION = 0.6;

    @Override
    public void onEnable() {
        getServer().getPluginManager().registerEvents(this, this);
        getLogger().info("MaceSmoke enabled. Mace hits now release a smoke ring from the torso.");
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

        // Launch from the victim's torso (chest height).
        Location torso = event.getEntity().getLocation()
                .add(0, event.getEntity().getHeight() * TORSO_FRACTION, 0);

        playHitSounds(torso);
        spawnExpandingSmokeRing(torso);
    }

    private void playHitSounds(Location loc) {
        World world = loc.getWorld();
        if (world == null) {
            return;
        }
        // Heavy mace smash — the core impact.
        world.playSound(loc, Sound.ITEM_MACE_SMASH_GROUND_HEAVY, SoundCategory.PLAYERS, 1.4f, 1.0f);
        // Deep metallic thud for weight.
        world.playSound(loc, Sound.BLOCK_ANVIL_LAND, SoundCategory.PLAYERS, 0.7f, 0.5f);
        // Airy boom for the smoke burst.
        world.playSound(loc, Sound.ENTITY_GENERIC_EXPLODE, SoundCategory.PLAYERS, 0.6f, 1.3f);
    }

    private void spawnExpandingSmokeRing(Location center) {
        World world = center.getWorld();
        if (world == null) {
            return;
        }

        new BukkitRunnable() {
            double radius = START_RADIUS;

            @Override
            public void run() {
                if (radius > MAX_RADIUS) {
                    cancel();
                    return;
                }

                for (int i = 0; i < POINTS_PER_RING; i++) {
                    double angle = (2 * Math.PI / POINTS_PER_RING) * i;
                    double x = Math.cos(angle) * radius;
                    double z = Math.sin(angle) * radius;
                    Location point = center.clone().add(x, 0, z);

                    // count > 0 with zero speed places packed particles that
                    // linger where they spawn instead of flying off.
                    world.spawnParticle(Particle.CLOUD, point, 2, 0.05, 0.05, 0.05, 0.0);
                }

                radius += EXPAND_PER_TICK;
            }
        }.runTaskTimer(this, 0L, 1L);
    }
}
