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

/**
 * When a player lands a mace slam from at least 5 blocks up, a single packed
 * ring of cloud-particle smoke bursts from the victim's torso and pans straight
 * outward, accompanied by heavy impact sounds.
 */
public class MaceSmokePlugin extends JavaPlugin implements Listener {

    // The attacker must have fallen at least this many blocks for the effect to
    // fire, so a normal ground hit does nothing.
    private static final double MIN_FALL_HEIGHT = 5.0;
    // How fast the single ring pans outward from the torso.
    private static final double OUTWARD_SPEED = 0.5;
    // Particles around the ring. Higher = more packed.
    private static final int POINTS_PER_RING = 64;
    // Radius the ring starts at, right around the body.
    private static final double START_RADIUS = 0.4;
    // Fraction of the victim's height to use as the torso point (~chest level).
    private static final double TORSO_FRACTION = 0.6;

    @Override
    public void onEnable() {
        getServer().getPluginManager().registerEvents(this, this);
        getLogger().info("MaceSmoke enabled. Mace slams from 5+ blocks release a smoke ring.");
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

        // Only fire on a real slam from height, not a hit while on the ground.
        if (player.getFallDistance() < MIN_FALL_HEIGHT) {
            return;
        }

        // Launch from the victim's torso (chest height).
        Location torso = event.getEntity().getLocation()
                .add(0, event.getEntity().getHeight() * TORSO_FRACTION, 0);

        playHitSounds(torso);
        spawnSmokeRing(torso);
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
        // Whoosh of air for the smoke burst.
        world.playSound(loc, Sound.ENTITY_WIND_CHARGE_WIND_BURST, SoundCategory.PLAYERS, 1.2f, 1.0f);
    }

    private void spawnSmokeRing(Location center) {
        World world = center.getWorld();
        if (world == null) {
            return;
        }

        // One ring: each particle starts on the ring and is given an outward
        // horizontal velocity, so a single ring pans straight out from the body.
        for (int i = 0; i < POINTS_PER_RING; i++) {
            double angle = (2 * Math.PI / POINTS_PER_RING) * i;
            double dirX = Math.cos(angle);
            double dirZ = Math.sin(angle);
            Location point = center.clone().add(dirX * START_RADIUS, 0, dirZ * START_RADIUS);

            // count = 0 makes the offset act as a velocity vector and the final
            // argument the speed, so the particle flies outward (no rising).
            world.spawnParticle(Particle.CLOUD, point, 0, dirX, 0.0, dirZ, OUTWARD_SPEED);
        }
    }
}
