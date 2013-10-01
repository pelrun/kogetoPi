depth = 3.5;
hole_r = 1.4;
kogeto_r_min = 5.4;
kogeto_r_max = 36/2;

difference()
{
	baseblock();
	translate([25/2, 14.5, -0.1]) cylinder(r=kogeto_r_min,h=depth+1);
}

module baseblock()
{
	cube([25,24,depth]);
	translate([25/2, 14.5, 0]) cylinder(r2=kogeto_r_max-9, r1=kogeto_r_max, h=depth);
}

