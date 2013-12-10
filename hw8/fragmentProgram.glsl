#version 120
uniform float t;
varying float u, v;

const float pi = 3.1415926535;
const float alpha = pi / 2;
const float beta = 0.15;

uniform sampler2D sky;
uniform sampler2D leaf;
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
   vec2 texCoords;

   // invert u and v from vertex shader
   float x = u*5 / pi / 2;
   float y = v*5 / pi / 2;

   // calculate normals in fragment shader
   if (useFragment < 0)
   {
      float Nx = 2 * alpha * beta * x * sin( alpha * (x * x + y * y + t));
      float Ny = 2 * alpha * beta * y * sin( alpha * (x * x + y * y + t));
      texCoords = unit(Nx, Ny);
   }
   // use normals from vertex shader
   else
   {
      texCoords = gl_TexCoord[0].xy;
   }	
   
   // blend sky reflection and leaf colors together
   vec4 skyColor = texture2D(sky, texCoords);
   vec4 leafColor = texture2D(leaf, vec2(x/5,-y/5));
   float alpha = leafColor.a;
   gl_FragColor = alpha * leafColor + (1 - alpha) * skyColor;
}
