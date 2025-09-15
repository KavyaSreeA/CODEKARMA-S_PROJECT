const html = `
<div id="scene-container" style="width:100%;height:600px;"></div>
<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script>
  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(75, window.innerWidth/window.innerHeight, 0.1, 1000);
  const renderer = new THREE.WebGLRenderer();
  renderer.setSize(window.innerWidth, 600);
  document.getElementById("scene-container").appendChild(renderer.domElement);

  // Shooter (cube for body, cylinder for gun)
  const body = new THREE.Mesh(new THREE.BoxGeometry(1,2,1), new THREE.MeshBasicMaterial({color: 0x0000ff}));
  body.position.set(0,1,0);
  scene.add(body);

  const gun = new THREE.Mesh(new THREE.CylinderGeometry(0.1,0.1,2,16), new THREE.MeshBasicMaterial({color: 0x333333}));
  gun.rotation.z = Math.PI / 2;
  gun.position.set(1.5,1.2,0);
  scene.add(gun);

  // Bullet
  const bullet = new THREE.Mesh(new THREE.SphereGeometry(0.1,16,16), new THREE.MeshBasicMaterial({color: 0xff0000}));
  bullet.position.set(1.5,1.2,0);
  scene.add(bullet);

  // Lighting
  const light = new THREE.DirectionalLight(0xffffff, 1);
  light.position.set(5,10,5);
  scene.add(light);

  camera.position.z = 10;

  // Physics parameters (will be replaced dynamically)
  let windSpeed = 10;  // m/s
  let windDir = 0;     // degrees
  let bulletSpeed = 50;
  let g = 9.81;

  let t = 0;
  function animate() {
    requestAnimationFrame(animate);
    t += 0.05;
    let rad = windDir * Math.PI / 180;

    let vx = bulletSpeed * Math.cos(rad) + windSpeed * Math.cos(rad);
    let vy = windSpeed * Math.sin(rad);
    let vz = 10;  // upward force

    bullet.position.x = 1.5 + vx * t;
    bullet.position.y = 1.2 + vy * t;
    bullet.position.z = vz * t - 0.5 * g * t * t;

    renderer.render(scene, camera);
  }
  animate();
</script>
`;

const targetOrigin = window.location.origin;

window.parent.postMessage({type: 'streamlit:componentReady'}, targetOrigin);
window.parent.postMessage({type: 'streamlit:setComponentValue', value: html}, targetOrigin);

