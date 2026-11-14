import { NodeIO } from '@gltf-transform/core';
import { ALL_EXTENSIONS } from '@gltf-transform/extensions';
const io = new NodeIO().registerExtensions(ALL_EXTENSIONS);
const items = { sofa:['sofa_02',0], armchair:['modern_arm_chair_01',0], lounge:['mid_century_lounge_chair',0], dining:['dining_chair_02',0],
  roundtable:['coffee_table_round_01',0], coffeetable:['modern_coffee_table_01',90], sidetable:['side_table_01',0], shelves:['wooden_display_shelves_01',90] };
for (const [out,[src,deg]] of Object.entries(items)) {
  const doc = await io.read(`out/${src}.glb`); const scene = doc.getRoot().listScenes()[0];
  if (deg) { const pivot = doc.createNode('pivot').setRotation([0, Math.sin(deg*Math.PI/360), 0, Math.cos(deg*Math.PI/360)]);
    for (const n of scene.listChildren()) { scene.removeChild(n); pivot.addChild(n); } scene.addChild(pivot); }
  await io.write(`final/${out}.glb`, doc); console.log(out, deg);
}
