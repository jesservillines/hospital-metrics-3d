import { useEffect } from 'react';
import * as THREE from 'three';
import { useThree } from '@react-three/fiber';
import { Sky } from '@react-three/drei';

export const Environment = () => {
  const { scene } = useThree();

  // Create gradient ground material
  const gradientCanvas = document.createElement('canvas');
  gradientCanvas.width = 128;
  gradientCanvas.height = 128;
  const ctx = gradientCanvas.getContext('2d')!;
  const gradient = ctx.createRadialGradient(64, 64, 0, 64, 64, 64);
  gradient.addColorStop(0, '#e5e5e5');
  gradient.addColorStop(1, '#d1d1d1');
  ctx.fillStyle = gradient;
  ctx.fillRect(0, 0, 128, 128);

  const gradientTexture = new THREE.CanvasTexture(gradientCanvas);
  gradientTexture.wrapS = gradientTexture.wrapT = THREE.RepeatWrapping;
  gradientTexture.repeat.set(100, 100);

  // Create grid pattern for ground detail
  const gridCanvas = document.createElement('canvas');
  gridCanvas.width = 512;
  gridCanvas.height = 512;
  const gridCtx = gridCanvas.getContext('2d')!;
  gridCtx.strokeStyle = '#cccccc';
  gridCtx.lineWidth = 1;

  // Draw grid
  for (let i = 0; i <= 512; i += 32) {
    gridCtx.beginPath();
    gridCtx.moveTo(i, 0);
    gridCtx.lineTo(i, 512);
    gridCtx.stroke();
    gridCtx.beginPath();
    gridCtx.moveTo(0, i);
    gridCtx.lineTo(512, i);
    gridCtx.stroke();
  }

  const gridTexture = new THREE.CanvasTexture(gridCanvas);
  gridTexture.wrapS = gridTexture.wrapT = THREE.RepeatWrapping;
  gridTexture.repeat.set(50, 50);

  useEffect(() => {
    // Set up scene background color instead of fog
    scene.background = new THREE.Color('#e0e0e0');

    // Add distance-based color grading effect
    const colorGrading = {
      near: new THREE.Color('#ffffff'),
      far: new THREE.Color('#e0e0e0')
    };

    // Update materials to use color grading
    scene.traverse((object) => {
      if (object instanceof THREE.Mesh && object.material instanceof THREE.MeshStandardMaterial) {
        object.material.onBeforeCompile = (shader) => {
          shader.uniforms.nearColor = { value: colorGrading.near };
          shader.uniforms.farColor = { value: colorGrading.far };
          shader.vertexShader = `
            varying float vDistance;
            ${shader.vertexShader}
          `.replace(
            '#include <project_vertex>',
            `
              #include <project_vertex>
              vDistance = length(mvPosition.xyz);
            `
          );

          shader.fragmentShader = `
            uniform vec3 nearColor;
            uniform vec3 farColor;
            varying float vDistance;
            ${shader.fragmentShader}
          `.replace(
            '#include <dithering_fragment>',
            `
              #include <dithering_fragment>
              float distanceFactor = smoothstep(50.0, 150.0, vDistance);
              gl_FragColor.rgb = mix(gl_FragColor.rgb, farColor, distanceFactor);
            `
          );
        };
      }
    });

    return () => {
      scene.background = null;
    };
  }, [scene]);

  return (
    <>
      {/* Sky */}
      <Sky
        distance={450000}
        sunPosition={[0, 1, 0]}
        inclination={0.6}
        azimuth={0.1}
        turbidity={10}
        rayleigh={2}
        mieCoefficient={0.005}
        mieDirectionalG={0.7}
      />

      {/* Ground plane with gradient and grid */}
      <mesh rotation-x={-Math.PI / 2} receiveShadow position={[0, -0.1, 0]}>
        <planeGeometry args={[1000, 1000]} />
        <meshStandardMaterial
          color="#ffffff"
          roughness={0.8}
          metalness={0.1}
          map={gradientTexture}
          alphaMap={gridTexture}
          transparent
          opacity={0.9}
        />
      </mesh>

      {/* Improved lighting */}
      <ambientLight intensity={0.4} />
      <directionalLight
        position={[50, 50, 25]}
        intensity={0.8}
        castShadow
        shadow-mapSize-width={2048}
        shadow-mapSize-height={2048}
        shadow-camera-far={100}
        shadow-camera-left={-50}
        shadow-camera-right={50}
        shadow-camera-top={50}
        shadow-camera-bottom={-50}
      />
    </>
  );
};