#version 120
uniform float t;
const float pi = 3.1415926535;
const float alpha = pi / 2;
const float beta = 0.15;

varying float u, v;
uniform int useFragment;

vec2 unit(float Nx, float Ny)
{
   // include z coordinate (1) in magnitude
   float mag = sqrt(Nx * Nx + Ny * Ny + 1);
   // shift unit vector by 0.5
   return vec2(Nx / mag + 0.5, Ny / mag + 0.5);
}

void main()
{
   float x = gl_Vertex.x;
   float y = gl_Vertex.y;

   // convert from x and y to u and v
   u = x / 5 * pi * 2;
   v = y / 5 * pi * 2;
   float height = beta * cos(alpha * (v*v + u*u + t));
   vec3 world = vec3(u, v, height);

   if (useFragment > 0)
   {
      // calculate normals in vertex shader
      float Nx = 2 * alpha * beta * x * sin( alpha * (x * x + y * y + t));
      float Ny = 2 * alpha * beta * y * sin( alpha * (x * x + y * y + t));
      gl_TexCoord[0].st = unit(Nx, Ny);
   }

   gl_Position = gl_ModelViewProjectionMatrix * vec4(world,1.0);
}
