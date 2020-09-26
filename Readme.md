TODO list
Features
- Fix so that spread water works in game engine aswell so that it becomes more dynamic.
- Only allow placing of blocks in unoccupied space
- Only render entities that is hit with light ray
- Make rays scatter when they hit a corner, so that lighting becomes more natural
- Add a hud for my items
- Make generic backdrop areas, needs to be able to calculate where different biomes start / end and draw to the backdrop 
    - Create a function that creates biome chunks, to be able to create the backdrop nicely
- I want to have an inventory
- Start using numpy instead of doing stuff urself.
- Fix raytracing to become more consistent, probably the correct approach is to send a ray to every block that is closeby.
    * One solution to solve problem of slow computation speed is to not relaclulate light sources each lap, just hold in memory what illumination to give for each block and reapply it each lap. Keep track of how many blocks are in the area covered, and if nr blocks changes in its area, recalulate once for that lamp. this is a good solution to the light problem. I think another good idea is to use quadtree to do this search algorithm, the boundingbox solution I have right now is better then before, but still not very good for 45 degree angles.
       I think the best solution would be to use quadtree to do a fast search.
- Maybe add opacity property to each block, so that I can have such things as glass and leafs.
- Make spread water function work dynamically.
- Where spread water function is done, the lighting gets screwed up.

Bugs
- The reach that I use to select and remove blocks is really buggy, I thinkt he stepsize is to big. The problem might be that stepsize is the wrong approach.

Working on:
- Fix so that placing blocks will mark the block where you place at, to make it easier for user.

Completed:
- Spread water function is not working atm, make it happen
- Should only be able to place blocks close to me and adjecent to another block.
- Add aim line, to help user.
- Sun should be regarded as a lightsource, not my head
- Add different levels of illumination
- I want to have different types of blocks that i can place
- I want to build / break with same button, but it should depend on item
- Activate the water and make the ray casting penetrate water
