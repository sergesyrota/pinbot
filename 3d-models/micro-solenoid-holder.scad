// Minimum thickness of the wall around elements
wall=1.5;
// Mounting magnet dimensions.
magnet=[4,11,2.5];
// Number of magnets to build side by side, for added strength
num_magnets=2;
// Extra padding on top of magnet housing to make it harder to disconnect from the surface
magnet_extra_leverage=10;
// Coordinates of mounting holes, relative to a full solenoid frame
screw_mounts=[[2,3.8], [8,13.6]];
// Pinball button
button_height=6; // highest point, for mount to clear completely
button_travel=3; // from the higherst point, how much it can be pressed, when in the center (there is a dimple too)
solenoid_stroke=10; // Including idle state protrusion
// How much to move solenoid body away from the surface to account for button size and extra motion
solenoid_travel_offset=solenoid_stroke-button_travel+button_height-wall-magnet[2];

// Solenoid mounting screws
screw_head_d=5.5;
screw_body_d=2.5;
screw_length=17;
// How much can screw go into the frame of the solenoid
solenoid_thread_depth=2;
// Back-and forth adjustment to account for different button height
screw_adjustment=5;

// width of magnet mounts and solenoid mount should match
structure_width=max(
    (magnet[0]+wall)*num_magnets+wall,
    max(screw_mounts[0][0],screw_mounts[1][0])+wall*2
);

rotate([0,-90,0]) difference() {
    body();
    // magnet cutout
    for (i=[0:num_magnets-1]) {
        rotate([90,0,0]) translate([wall+i*(wall+magnet[0]), wall, wall]) cube(magnet);
    }
    // screw hole
    for (s=screw_mounts) {
        #translate(
            // ALl this complex calculation to place it in the middle of the structure
            [(structure_width-max(screw_mounts[0][0], screw_mounts[1][0])-min(screw_mounts[0][0], screw_mounts[1][0]))/2+s[0], 
            s[1]+solenoid_travel_offset, 
            wall]
        ) screw_mount();
    }
    // space for the button
    translate([0,-magnet[2]-wall,-screw_length]) cube([structure_width, button_height, screw_length]);
}

// Solid body, from which we will cut pieces out
module body() {
    union() {
        // padding for the screw length, so that it does not go deeper than solenoid_thread_depth
        extra_padding=screw_length-solenoid_thread_depth-wall;
        // solenoid mount body
        translate([0,solenoid_travel_offset-screw_adjustment/2,-extra_padding]) cube([
            structure_width, 
            max(screw_mounts[0][1],screw_mounts[1][1])+screw_adjustment+wall*2,
            wall+extra_padding+5]); // 5 for extra overlap with magnets
        // Magnet holder
        // Making sure we contact solenoid body too
        contact_adjustment=solenoid_travel_offset-screw_adjustment/2;
        rotate([90,0,0]) 
            translate([0,0,-contact_adjustment]) 
            cube([structure_width, magnet_extra_leverage+magnet[1]+wall*2, magnet[2]+wall+contact_adjustment]);
    }
}

// Cutout that needs to be made for the screw, including head depth, and length, and some wiggle room
module screw_mount() {
    // screw head
    translate([-screw_head_d/2, -(screw_head_d+screw_adjustment)/2, 0]) cube([screw_head_d, screw_head_d+screw_adjustment,max(magnet)]);
    // screw body
    translate([-screw_body_d/2, -(screw_body_d+screw_adjustment)/2, -screw_length]) cube([screw_body_d, screw_body_d+screw_adjustment,screw_length]);    
}