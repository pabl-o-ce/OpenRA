# Heavy industrial refinement

This pass strengthens the original Furnace Covenant visual language in response
to the request for more imposing, brutal military machinery. The reference is
the weight and monumental scale of dark science-fiction warfare. Shapes,
markings, models and symbols remain our own.

## Shape and material rules

- Primary forms carry the design at RTS zoom: broad track armor, a faceted
  turret, deep portal beams, buttresses and shielded exhaust towers.
- Pale refractory armor covers critical surfaces. Dark structural iron shows
  through joints, recesses and exposed machinery. Oxide red marks heat shields
  and replaceable components.
- Repeat a few large structural details; concentrate smaller studs, chips and
  abrasions around exposed edges. Preserve quiet surfaces between them.
- Use cyan for induction equipment and amber for work lights. Player colors
  occupy distinct panels with enough visible area to identify ownership.
- Retain the three-upright foundry stamp and practical identification numbers.
  The architecture is fortified industry, built around pressure and heat.

## Implemented in this pass

The K-6 has a taller, faceted turret; layered track skirts; a reinforced prow;
towing points; radiator cowls; a recessed muzzle; and a smaller protected charge
aperture. The factory gains six sloped buttresses, shielded exhaust towers,
heavier door piers, a projecting entrance beam, and a raised roof manifold.
Its existing fan and shutter animations remain.
The damaged factory has scorched supports and a collapsed exhaust crown, so
its damage state remains distinct even with the darker normal roof.

This is a visual revision of the same actors. Armor statistics, weapon damage,
footprints, costs and movement are unchanged. The skirts are protective armor,
not additional weapons. The observation hatch is not a secondary turret.

## Reproduction and rollback

Use Blender MCP to load `tools/heavy_visuals.py` with `importlib`, store the
module as `bpy.app.driver_namespace['fc_heavy_pass']`, call `build()`, and then
`start_render('sprites')`. It builds only new scenes, using the earlier helper
module for camera, lighting, frame anchors and rendering. Wait for
`art/heavy/render-status.json` to report all **127** frames complete. Then call
`start_render('previews')` for the two presentation views.

```sh
ENGINE_DIR="$PWD" python3 mods/pvphit/tools/pack_refined_assets.py \
  --pass-name heavy --dotnet dotnet
```

Editable models are in `art/source/heavy/`. Sheets and metadata are under
`art/heavy/`, with final overrides in `sequences/heavy.yaml`. The earlier models
and sheets are preserved. Removing the `sequences/heavy.yaml` manifest entry
restores the previous tank and factory visuals.

Review the new forms in `foundry-visual-yard` before applying this treatment to
the rest of the roster. Next priorities are faction-wide silhouette consistency,
articulated track motion, physical damage/wreck geometry, more substantial
construction animation, and a coherent industrial terrain set.
