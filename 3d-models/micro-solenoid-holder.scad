wall=3;
magnet=[12,5,2];
screw_mounts=[[3,2], [7,15]];
// How much to move solenoid body away from the surface to account for button size and extra motion
solenoid_travel_offset=10;
button_height=12;

screw_head_d=7;
screw_body_d=3;
screw_length=10;
solenoid_thread_depth=3;

rotate([0,270,0]) difference() {
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
        translate([0,solenoid_travel_offset,-extra_padding]) cube([
            max(screw_mounts[0][0],screw_mounts[1][0])+wall*2, 
            max(screw_mounts[0][1],screw_mounts[1][1])+wall*2,
            wall+extra_padding]);
        // Magnet holder
        rotate([90,0,0]) cube([magnet[0]+wall*2, magnet[1]+wall*2, magnet[2]+wall]);
    }
}

// Cutout that needs to be made for the screw, including head depth, and length
module screw_mount() {
    // screw head
    cylinder(d=screw_head_d, h=max(magnet));
    // screw body
    translate([0,0,-screw_length]) cylinder(d=screw_body_d, h=screw_length);
}