mod-title = PvPHit: Furnace Covenant Prototype
mod-windowtitle = OpenRA - PvPHit: Furnace Covenant Prototype

# Mod-local connection identity; account endpoints and authentication logic are unchanged.
label-connecting-panel-title = Connecting to a PvPHit game
label-connecting-to-endpoint = Connecting to PvPHit server { $endpoint }...
label-could-not-connect-to-target = Could not connect to PvPHit server { $target }.
label-connection-failed = PvPHit connection failed
faction-kiln =
    .name = Kiln Directorate
    .description = Rival expeditionary foundries fighting to sustain Veyr's industrial settlements.

actor-fc-tank =
    .name = K-6 Induction Tank
    .description =
        Armored direct-fire vehicle.
        Strong against armor; vulnerable to concentrated fire.
actor-fc-tank-husk = Induction Tank Wreck
actor-fc-scout =
    .name = Relay Scout
    .description =
        Fast reconnaissance and facility capture.
        Capture takes five seconds; scout survives.
actor-fc-hauler =
    .name = Slag Hauler
    .description = Collects mineral slag and delivers it to a processor.
actor-fc-siege =
    .name = Brace Mortar Carrier
    .description =
        Deploy to bombard structures.
        Two-second setup and withdrawal; cannot fire while moving.
actor-fc-hq =
    .name = Foundry Headquarters
actor-fc-generator =
    .name = Pressure Generator
    .description = Supplies 100 power to the foundry.
actor-fc-processor =
    .name = Slag Processor
    .description =
        Processes mineral slag. Includes one Slag Hauler.
        Requires 30 power.
actor-fc-factory =
    .name = Armor Works
    .description =
        Manufactures Directorate vehicles.
        Requires 50 power.
actor-fc-facility =
    .name = Pressure Metering Station
