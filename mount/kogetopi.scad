depth = 10;
hole_r = 1.4;
kogeto_r_min = 5.4;
kogeto_r_max = 36/2;

difference()
{
	baseblock();
	translate([7.5,1,depth-6]) cube([10,21,7]);
	translate([18.5,-1,depth-1]) cube([8,8,2]);
}
translate([7.5,0,0]) cube([10,5,8]);

difference()
{
	translate([25/2, 14.5, 0]) cylinder(r2=kogeto_r_max-12, r1=kogeto_r_max, h=depth);
	translate([0,0,-0.1]) cube([25,24,depth+0.2]);

}

module baseblock()
{
	difference()
	{
		cube([25,24,depth]);
		translate([25/2, 14.5, -0.1]) cylinder(r=kogeto_r_min,h=depth+0.2);
		for (x=[2,23])
			for (y=[2,14.5])
				translate([x,y,-0.1])
					cylinder(r=hole_r,h=depth+0.2);
	}
}

