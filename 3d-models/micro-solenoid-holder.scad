wall=2;
magnet=[11,4,2.5];
screw_mounts=[[2,3.8], [8,13.6]];
// How much to move solenoid body away from the surface to account for button size and extra motion
solenoid_travel_offset=1.5+6-wall-magnet[2];
button_height=6;

screw_head_d=5.5;
screw_body_d=2.5;
screw_length=17;
solenoid_thread_depth=2;
screw_adjustment=5;

rotate([0,-90,0]) difference() {
    body();
    // magnet cutout
    rotate([90,0,0]) translate([wall, wall, wall]) cube(magnet);
    // screw hole
    for (s=screw_mounts) {
        #translate([s[0], s[1]+solenoid_travel_offset, wall]) screw_mount();
    }
    // space for the button
    translate([0,-magnet[2]-wall,-screw_length]) cube([magnet[0]+wall*2, button_height, screw_length]);
}

// Solid body, from which we will cut pieces out
module body() {
    hull() {
        // padding for the screw length, so that it does not go deeper than solenoid_thread_depth
        extra_padding=screw_length-solenoid_thread_depth-wall;
        // solenoid mount body
        translate([0,solenoid_travel_offset-screw_adjustment/2,-extra_padding]) cube([
            max(screw_mounts[0][0],screw_mounts[1][0])+wall*2, 
            max(screw_mounts[0][1],screw_mounts[1][1])+screw_adjustment+wall*2,
            wall+extra_padding]);
        // Magnet holder
        rotate([90,0,0]) cube([magnet[0]+wall*2, magnet[1]+wall*2, magnet[2]+wall]);
    }
}

// Cutout that needs to be made for the screw, including head depth, and length, and some wiggle room
module screw_mount() {
    // screw head
    translate([-screw_head_d/2, -(screw_head_d+screw_adjustment)/2, 0]) cube([screw_head_d, screw_head_d+screw_adjustment,max(magnet)]);
    // screw body
    translate([-screw_body_d/2, -(screw_body_d+screw_adjustment)/2, -screw_length]) cube([screw_body_d, screw_body_d+screw_adjustment,screw_length]);    
}