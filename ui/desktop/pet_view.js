/* ==========================================================================
   CAPTAIN AI OS 2.0 — DESKTOP ROBOT PET WEBGL VIEW
   Reuses the EXISTING 3D EMO Desktop AI Robot Pet from ui/web/app.js.
   ZERO REDESIGN: Exact same geometry, materials, shaders, LED expressions,
   lip-sync mouth engine, foot motion, and floating physics.
   ========================================================================== */

(function () {
    let scene, camera, renderer, coreGroup;
    let threeCanvas = document.getElementById('pet-canvas');
    let isSpeakingState = false;
    let currentExpression = 'happy';
    let currentAudioAmplitude = 0.0;
    let isBlinkingState = false;
    let lastBlink = Date.now();
    let startTime = Date.now();

    function initThreeJS() {
        if (!window.THREE || !threeCanvas) return false;

        scene = new THREE.Scene();
        window.globalScene = scene;

        camera = new THREE.PerspectiveCamera(52, window.innerWidth / window.innerHeight, 0.1, 1000);
        camera.position.z = 6.2;
        camera.position.y = 0.1;

        renderer = new THREE.WebGLRenderer({
            canvas: threeCanvas,
            antialias: true,
            alpha: true
        });
        renderer.setSize(window.innerWidth, window.innerHeight);
        renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));

        window.addEventListener('resize', () => {
            if (!camera || !renderer) return;
            camera.aspect = window.innerWidth / window.innerHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(window.innerWidth, window.innerHeight);
        });

        coreGroup = new THREE.Group();
        scene.add(coreGroup);

        // --- 3D EMO Desktop AI Robot Pet Character System ---
        const faceCanvas = document.createElement('canvas');
        faceCanvas.width = 256;
        faceCanvas.height = 256;
        const faceCtx = faceCanvas.getContext('2d');
        const faceTexture = new THREE.CanvasTexture(faceCanvas);

        function roundRect(ctx, x, y, width, height, radius) {
            ctx.beginPath();
            ctx.moveTo(x + radius, y);
            ctx.lineTo(x + width - radius, y);
            ctx.quadraticCurveTo(x + width, y, x + width, y + radius);
            ctx.lineTo(x + width, y + height - radius);
            ctx.quadraticCurveTo(x + width, y + height, x + width - radius, y + height);
            ctx.lineTo(x + radius, y + height);
            ctx.quadraticCurveTo(x, y + height, x, y + height - radius);
            ctx.lineTo(x, y + radius);
            ctx.quadraticCurveTo(x, y, x + radius, y);
            ctx.closePath();
            ctx.fill();
        }

        function drawHeart(ctx, cx, cy, size) {
            ctx.beginPath();
            ctx.moveTo(cx, cy + size * 0.35);
            ctx.bezierCurveTo(cx - size * 0.6, cy - size * 0.1, cx - size * 0.7, cy - size * 0.7, cx, cy - size * 0.4);
            ctx.bezierCurveTo(cx + size * 0.7, cy - size * 0.7, cx + size * 0.6, cy - size * 0.1, cx, cy + size * 0.35);
            ctx.fill();
        }

        function drawStar(ctx, cx, cy, spikes, outerRadius, innerRadius) {
            let rot = Math.PI / 2 * 3;
            let step = Math.PI / spikes;
            ctx.beginPath();
            ctx.moveTo(cx, cy - outerRadius);
            for (let i = 0; i < spikes; i++) {
                let x = cx + Math.cos(rot) * outerRadius;
                let y = cy + Math.sin(rot) * outerRadius;
                ctx.lineTo(x, y);
                rot += step;

                x = cx + Math.cos(rot) * innerRadius;
                y = cy + Math.sin(rot) * innerRadius;
                ctx.lineTo(x, y);
                rot += step;
            }
            ctx.lineTo(cx, cy - outerRadius);
            ctx.closePath();
            ctx.fill();
        }

        function drawRobotFace(expression) {
            faceCtx.fillStyle = '#080a0f';
            faceCtx.fillRect(0, 0, 256, 256);

            faceCtx.fillStyle = '#00f2fe';
            faceCtx.strokeStyle = '#00f2fe';
            faceCtx.shadowColor = '#00f2fe';
            faceCtx.shadowBlur = 20;
            faceCtx.lineWidth = 10;
            faceCtx.lineCap = 'round';

            if (isBlinkingState) {
                // Slim blinking eyes
                roundRect(faceCtx, 46, 110, 64, 16, 8);
                roundRect(faceCtx, 146, 110, 64, 16, 8);
                faceCtx.beginPath(); faceCtx.moveTo(110, 165); faceCtx.lineTo(146, 165); faceCtx.stroke();
                faceTexture.needsUpdate = true;
                return;
            }

            switch (expression) {
                case 'cool': // 😎 Cool Sunglasses / Listening Mode
                    faceCtx.fillStyle = '#00f2fe';
                    roundRect(faceCtx, 36, 80, 80, 50, 10);
                    roundRect(faceCtx, 140, 80, 80, 50, 10);
                    faceCtx.beginPath(); faceCtx.moveTo(116, 95); faceCtx.lineTo(140, 95); faceCtx.stroke();
                    if (currentAudioAmplitude > 0.05) {
                        const ripple = Math.min(22, Math.floor(currentAudioAmplitude * 28));
                        faceCtx.lineWidth = 4;
                        faceCtx.beginPath();
                        faceCtx.arc(76, 105, 30 + ripple, 0, Math.PI * 2);
                        faceCtx.arc(180, 105, 30 + ripple, 0, Math.PI * 2);
                        faceCtx.stroke();
                        faceCtx.lineWidth = 10;
                    }
                    faceCtx.beginPath(); faceCtx.arc(135, 165, 18, Math.PI * 0.1, Math.PI * 0.7); faceCtx.stroke();
                    break;


                case 'crying': // 😭 Crying Tears
                    faceCtx.lineWidth = 12;
                    faceCtx.beginPath(); faceCtx.moveTo(46, 100); faceCtx.lineTo(106, 118); faceCtx.stroke();
                    faceCtx.beginPath(); faceCtx.moveTo(210, 100); faceCtx.lineTo(150, 118); faceCtx.stroke();
                    faceCtx.fillStyle = '#00f2fe';
                    faceCtx.beginPath(); faceCtx.arc(76, 140, 8, 0, Math.PI * 2); faceCtx.fill();
                    faceCtx.beginPath(); faceCtx.arc(176, 140, 8, 0, Math.PI * 2); faceCtx.fill();
                    faceCtx.beginPath(); faceCtx.arc(128, 185, 20, Math.PI * 1.15, Math.PI * 1.85); faceCtx.stroke();
                    break;

                case 'laughing': // 😆 Laughing Squeezed > <
                    faceCtx.lineWidth = 14;
                    faceCtx.beginPath(); faceCtx.moveTo(50, 90); faceCtx.lineTo(95, 110); faceCtx.lineTo(50, 130); faceCtx.stroke();
                    faceCtx.beginPath(); faceCtx.moveTo(206, 90); faceCtx.lineTo(161, 110); faceCtx.lineTo(206, 130); faceCtx.stroke();
                    faceCtx.beginPath(); faceCtx.arc(128, 160, 22, 0, Math.PI); faceCtx.fill();
                    break;

                case 'angry': // 😤 Angry Frustrated
                    faceCtx.lineWidth = 14;
                    faceCtx.beginPath(); faceCtx.moveTo(46, 80); faceCtx.lineTo(106, 105); faceCtx.stroke();
                    faceCtx.beginPath(); faceCtx.moveTo(210, 80); faceCtx.lineTo(150, 105); faceCtx.stroke();
                    roundRect(faceCtx, 46, 110, 64, 30, 8);
                    roundRect(faceCtx, 146, 110, 64, 30, 8);
                    faceCtx.lineWidth = 8;
                    faceCtx.beginPath(); faceCtx.moveTo(100, 175); faceCtx.lineTo(114, 165); faceCtx.lineTo(128, 175); faceCtx.lineTo(142, 165); faceCtx.lineTo(156, 175); faceCtx.stroke();
                    break;

                case 'shy': // 🥹 Shy Blushing Cheeks
                    faceCtx.fillStyle = 'rgba(255, 100, 150, 0.85)';
                    faceCtx.beginPath(); faceCtx.arc(50, 135, 16, 0, Math.PI * 2); faceCtx.fill();
                    faceCtx.beginPath(); faceCtx.arc(206, 135, 16, 0, Math.PI * 2); faceCtx.fill();
                    faceCtx.fillStyle = '#00f2fe';
                    roundRect(faceCtx, 60, 88, 50, 50, 15);
                    roundRect(faceCtx, 146, 88, 50, 50, 15);
                    faceCtx.beginPath(); faceCtx.arc(128, 165, 10, 0, Math.PI); faceCtx.stroke();
                    break;

                case 'thinking': // 🧐 Monocle Thinking
                    faceCtx.lineWidth = 6;
                    faceCtx.beginPath(); faceCtx.arc(178, 105, 36, 0, Math.PI * 2); faceCtx.stroke();
                    faceCtx.beginPath(); faceCtx.moveTo(150, 60); faceCtx.lineTo(206, 60); faceCtx.stroke();
                    roundRect(faceCtx, 46, 88, 54, 54, 16);
                    faceCtx.lineWidth = 10;
                    faceCtx.beginPath(); faceCtx.moveTo(110, 170); faceCtx.lineTo(146, 160); faceCtx.stroke();
                    break;

                case 'secret': // 🤫 Quiet Secretive Shh
                    faceCtx.beginPath(); faceCtx.arc(78, 115, 26, Math.PI * 1.1, Math.PI * 1.9); faceCtx.stroke();
                    roundRect(faceCtx, 146, 78, 64, 64, 18);
                    faceCtx.fillStyle = '#00f2fe';
                    roundRect(faceCtx, 120, 145, 16, 45, 8);
                    break;

                case 'salute': // 🫡 Respectful Salute
                    roundRect(faceCtx, 46, 88, 64, 64, 18);
                    roundRect(faceCtx, 146, 88, 64, 64, 18);
                    faceCtx.lineWidth = 12;
                    faceCtx.beginPath(); faceCtx.moveTo(140, 65); faceCtx.lineTo(215, 65); faceCtx.stroke();
                    faceCtx.beginPath(); faceCtx.moveTo(105, 165); faceCtx.lineTo(151, 165); faceCtx.stroke();
                    break;

                case 'tired': // 😮‍💨 Tired Relieved
                    faceCtx.lineWidth = 10;
                    faceCtx.beginPath(); faceCtx.moveTo(46, 110); faceCtx.lineTo(110, 100); faceCtx.stroke();
                    faceCtx.beginPath(); faceCtx.moveTo(146, 100); faceCtx.lineTo(210, 110); faceCtx.stroke();
                    faceCtx.beginPath(); faceCtx.arc(128, 165, 12, 0, Math.PI * 2); faceCtx.stroke();
                    faceCtx.beginPath(); faceCtx.moveTo(145, 165); faceCtx.quadraticCurveTo(160, 160, 170, 168); faceCtx.stroke();
                    break;

                case 'neutral': // 😑 Neutral Unimpressed
                    faceCtx.lineWidth = 12;
                    faceCtx.beginPath(); faceCtx.moveTo(46, 110); faceCtx.lineTo(110, 110); faceCtx.stroke();
                    faceCtx.beginPath(); faceCtx.moveTo(146, 110); faceCtx.lineTo(210, 110); faceCtx.stroke();
                    faceCtx.beginPath(); faceCtx.moveTo(105, 165); faceCtx.lineTo(151, 165); faceCtx.stroke();
                    break;

                case 'smirk': // 😏 Smirking Playful
                    roundRect(faceCtx, 46, 80, 60, 60, 16);
                    roundRect(faceCtx, 146, 96, 60, 48, 16);
                    faceCtx.beginPath(); faceCtx.arc(135, 165, 20, Math.PI * 0.1, Math.PI * 0.75); faceCtx.stroke();
                    break;

                case 'surprised': // 😮 Surprised Shocked
                    faceCtx.beginPath(); faceCtx.arc(78, 110, 36, 0, Math.PI * 2); faceCtx.arc(178, 110, 36, 0, Math.PI * 2); faceCtx.fill();
                    faceCtx.beginPath(); faceCtx.arc(128, 178, 16, 0, Math.PI * 2); faceCtx.fill();
                    break;

                case 'love': // ♥ ♥ Heart Eyes
                    drawHeart(faceCtx, 78, 110, 36);
                    drawHeart(faceCtx, 178, 110, 36);
                    faceCtx.beginPath(); faceCtx.arc(128, 160, 22, Math.PI * 0.15, Math.PI * 0.85); faceCtx.stroke();
                    break;

                case 'star': // ★ ★ Star Eyes
                    drawStar(faceCtx, 78, 110, 5, 34, 16);
                    drawStar(faceCtx, 178, 110, 5, 34, 16);
                    faceCtx.beginPath(); faceCtx.arc(128, 160, 22, Math.PI * 0.15, Math.PI * 0.85); faceCtx.stroke();
                    break;

                case 'wink':
                case 'wave':
                    faceCtx.beginPath(); faceCtx.arc(78, 115, 26, Math.PI * 1.1, Math.PI * 1.9); faceCtx.stroke();
                    roundRect(faceCtx, 146, 78, 64, 64, 18);
                    faceCtx.beginPath(); faceCtx.arc(136, 165, 18, Math.PI * 0.15, Math.PI * 0.85); faceCtx.stroke();
                    break;

                case 'sleeping': // 😴 Sleeping / Standby Mode
                    faceCtx.lineWidth = 8;
                    faceCtx.beginPath(); faceCtx.arc(78, 115, 24, Math.PI * 0.1, Math.PI * 0.9); faceCtx.stroke();
                    faceCtx.beginPath(); faceCtx.arc(178, 115, 24, Math.PI * 0.1, Math.PI * 0.9); faceCtx.stroke();
                    faceCtx.font = '24px monospace';
                    faceCtx.fillText('z', 130, 160);
                    break;

                default: // Happy default
                    roundRect(faceCtx, 46, 78, 64, 64, 18);
                    roundRect(faceCtx, 146, 78, 64, 64, 18);

                    if (isSpeakingState) {
                        // Real-time Audio-Reactive Lip-Sync Mouth Engine
                        faceCtx.fillStyle = '#00f2fe';
                        const amp = Math.max(0.12, currentAudioAmplitude);
                        const mouthH = Math.min(26, Math.floor(7 + amp * 32));
                        const mouthW = Math.min(30, Math.floor(14 + amp * 18));
                        faceCtx.beginPath();
                        faceCtx.ellipse(128, 168, mouthW, mouthH, 0, 0, Math.PI * 2);
                        faceCtx.fill();
                    } else {
                        faceCtx.beginPath(); faceCtx.arc(128, 160, 22, Math.PI * 0.15, Math.PI * 0.85); faceCtx.stroke();
                    }
                    break;

            }

            faceTexture.needsUpdate = true;
        }

        drawRobotFace('happy');

        // 1. Robot Head Shell (Dark Charcoal Matte)
        const headGeo = new THREE.BoxGeometry(2.3, 2.1, 1.9);
        const headMat = new THREE.MeshBasicMaterial({ color: 0x1c1d22 });
        const headMesh = new THREE.Mesh(headGeo, headMat);
        coreGroup.add(headMesh);

        // Silver Visor Bezel Rim
        const bezelGeo = new THREE.PlaneGeometry(1.85, 1.45);
        const bezelMat = new THREE.MeshBasicMaterial({ color: 0x4a4d5a });
        const bezelMesh = new THREE.Mesh(bezelGeo, bezelMat);
        bezelMesh.position.z = 0.96;
        coreGroup.add(bezelMesh);

        // Visor Screen with Dynamic LED Facial Expressions
        const visorGeo = new THREE.PlaneGeometry(1.7, 1.3);
        const visorMat = new THREE.MeshBasicMaterial({ map: faceTexture, transparent: true });
        const visorMesh = new THREE.Mesh(visorGeo, visorMat);
        visorMesh.position.z = 0.97;
        coreGroup.add(visorMesh);

        // 2. Purple & Cyan Headband Headphones (Smooth Cubic Bezier Arch Clearing Head Shell)
        const headphoneCurve = new THREE.CubicBezierCurve3(
            new THREE.Vector3(-1.32, 0.2, 0),
            new THREE.Vector3(-1.45, 1.82, 0.05),
            new THREE.Vector3(1.45, 1.82, 0.05),
            new THREE.Vector3(1.32, 0.2, 0)
        );

        const headbandGeo = new THREE.TubeGeometry(headphoneCurve, 64, 0.11, 16, false);
        const headbandMat = new THREE.MeshBasicMaterial({ color: 0x4e2a84 });
        const headband = new THREE.Mesh(headbandGeo, headbandMat);
        coreGroup.add(headband);

        // Left & Right Earcups
        const earcupGeo = new THREE.CylinderGeometry(0.48, 0.48, 0.28, 32);
        const earcupMat = new THREE.MeshBasicMaterial({ color: 0x22242e });

        const earcupL = new THREE.Mesh(earcupGeo, earcupMat);
        earcupL.rotation.z = Math.PI / 2;
        earcupL.position.set(-1.25, 0.2, 0);
        coreGroup.add(earcupL);

        const earcupR = new THREE.Mesh(earcupGeo, earcupMat);
        earcupR.rotation.z = Math.PI / 2;
        earcupR.position.set(1.25, 0.2, 0);
        coreGroup.add(earcupR);

        // Glowing Cyan LED Ear Ring Lights
        const ringGeo = new THREE.TorusGeometry(0.4, 0.04, 16, 32);
        const ringMat = new THREE.MeshBasicMaterial({ color: 0x00f2fe });

        const ringL = new THREE.Mesh(ringGeo, ringMat);
        ringL.rotation.y = Math.PI / 2;
        ringL.position.set(-1.41, 0.2, 0);
        coreGroup.add(ringL);

        const ringR = new THREE.Mesh(ringGeo, ringMat);
        ringR.rotation.y = Math.PI / 2;
        ringR.position.set(1.41, 0.2, 0);
        coreGroup.add(ringR);

        // 3. Robot Feet
        const footGroup = new THREE.Group();
        const footGeo = new THREE.BoxGeometry(0.85, 0.38, 1.25);
        const footMat = new THREE.MeshBasicMaterial({ color: 0x16171d });

        const footL = new THREE.Mesh(footGeo, footMat);
        footL.position.set(-0.65, -1.35, 0.1);
        footGroup.add(footL);

        const footR = new THREE.Mesh(footGeo, footMat);
        footR.position.set(0.65, -1.35, 0.1);
        footGroup.add(footR);

        coreGroup.add(footGroup);

        // 4. Dark Cylindrical Circular Studio Stage Podium
        const podiumGroup = new THREE.Group();

        const shadowGeo = new THREE.RingGeometry(0.2, 1.6, 32);
        const shadowMat = new THREE.MeshBasicMaterial({ color: 0x06070a, side: THREE.DoubleSide, transparent: true, opacity: 0.85 });
        const shadowMesh = new THREE.Mesh(shadowGeo, shadowMat);
        shadowMesh.rotation.x = Math.PI / 2;
        shadowMesh.position.set(0, -1.535, 0.1);
        podiumGroup.add(shadowMesh);

        const topDiskGeo = new THREE.CylinderGeometry(3.6, 3.8, 0.45, 64);
        const topDiskMat = new THREE.MeshBasicMaterial({ color: 0x242733 });
        const topDiskMesh = new THREE.Mesh(topDiskGeo, topDiskMat);
        topDiskMesh.position.set(0, -1.765, 0);
        podiumGroup.add(topDiskMesh);

        const ringEdgeGeo = new THREE.TorusGeometry(3.65, 0.05, 16, 64);
        const ringEdgeMat = new THREE.MeshBasicMaterial({ color: 0x484e63 });
        const ringEdgeMesh = new THREE.Mesh(ringEdgeGeo, ringEdgeMat);
        ringEdgeMesh.rotation.x = Math.PI / 2;
        ringEdgeMesh.position.set(0, -1.54, 0);
        podiumGroup.add(ringEdgeMesh);

        const skirtGeo = new THREE.CylinderGeometry(3.8, 4.0, 1.2, 64);
        const skirtMat = new THREE.MeshBasicMaterial({ color: 0x0e1014 });
        const skirtMesh = new THREE.Mesh(skirtGeo, skirtMat);
        skirtMesh.position.set(0, -2.59, 0);
        podiumGroup.add(skirtMesh);

        scene.add(podiumGroup);

        scene.userData.drawRobotFace = drawRobotFace;
        scene.userData.footL = footL;
        scene.userData.footR = footR;

        return true;
    }

    const isLoaded = initThreeJS();

    function animate3D() {
        requestAnimationFrame(animate3D);
        const time = (Date.now() - startTime) * 0.001;

        if (isLoaded && renderer && scene && camera) {
            // Harmonic idle floating bob
            const floatOffsetY = Math.sin(time * 2.5) * 0.06;
            if (coreGroup) {
                coreGroup.position.y = floatOffsetY;
            }

            // Foot stepping motion
            if (scene.userData.footL && scene.userData.footR) {
                const stepL = Math.sin(time * 5.0) * 0.06;
                scene.userData.footL.position.y = -1.35 + Math.max(0, stepL);
                scene.userData.footR.position.y = -1.35 + Math.max(0, -stepL);
            }

            // Natural eye blinking timer (150ms every 3.2s)
            const now = Date.now();
            if (!isBlinkingState && now - lastBlink > 3200) {
                isBlinkingState = true;
                lastBlink = now;
                if (scene.userData.drawRobotFace) scene.userData.drawRobotFace(currentExpression);
            } else if (isBlinkingState && now - lastBlink > 160) {
                isBlinkingState = false;
                lastBlink = now;
                if (scene.userData.drawRobotFace) scene.userData.drawRobotFace(currentExpression);
            }

            // Lip-sync update during active speech
            if (isSpeakingState && scene.userData.drawRobotFace) {
                scene.userData.drawRobotFace(currentExpression);
            }

            renderer.render(scene, camera);
        }
    }

    animate3D();

    // =========================================================================
    // DESKTOP PYTHON RUNTIME BRIDGE APIs
    // =========================================================================
    window.setCaptainState = function (state) {
        state = (state || 'STANDBY').toUpperCase();
        switch (state) {
            case 'STANDBY':
                currentExpression = 'sleeping';
                isSpeakingState = false;
                break;
            case 'ACTIVE':
                currentExpression = 'happy';
                isSpeakingState = false;
                break;
            case 'LISTENING':
                currentExpression = 'cool'; // Attentive visor look
                isSpeakingState = false;
                break;
            case 'THINKING':
                currentExpression = 'thinking'; // Monocle thinking eye
                isSpeakingState = false;
                break;
            case 'OBSERVING':
                currentExpression = 'star'; // Analyzing screen
                isSpeakingState = false;
                break;
            case 'EXECUTING':
                currentExpression = 'salute'; // Focused execution
                isSpeakingState = false;
                break;
            case 'SPEAKING':
                currentExpression = 'happy';
                isSpeakingState = true; // Flaps mouth
                break;
            case 'ERROR':
                currentExpression = 'angry';
                isSpeakingState = false;
                break;
            default:
                currentExpression = 'happy';
                isSpeakingState = false;
        }
        if (scene && scene.userData.drawRobotFace) {
            scene.userData.drawRobotFace(currentExpression);
        }
    };

    window.setCaptainExpression = function (expr) {
        currentExpression = expr || 'happy';
        if (scene && scene.userData.drawRobotFace) {
            scene.userData.drawRobotFace(currentExpression);
        }
    };

    window.setSpeaking = function (speaking) {
        isSpeakingState = Boolean(speaking);
        if (!isSpeakingState) {
            currentAudioAmplitude = 0.0;
        }
        if (scene && scene.userData.drawRobotFace) {
            scene.userData.drawRobotFace(currentExpression);
        }
    };

    window.setAudioAmplitude = function (amplitude) {
        currentAudioAmplitude = Math.max(0.0, Math.min(1.0, Number(amplitude) || 0.0));
        if (currentAudioAmplitude > 0.04) {
            isSpeakingState = true;
        }
        if (scene && scene.userData.drawRobotFace) {
            scene.userData.drawRobotFace(currentExpression);
        }
    };
})();

