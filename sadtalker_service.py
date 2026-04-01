"""
SadTalker as a separate HTTP service
Run: python sadtalker_service.py
"""
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import sys
import uuid
import subprocess
from pathlib import Path
import shutil

app = Flask(__name__)
CORS(app)

SADTALKER_DIR = Path(__file__).parent
CHECKPOINTS_DIR = SADTALKER_DIR / 'checkpoints'
RESULTS_DIR = SADTALKER_DIR / 'results'
RESULTS_DIR.mkdir(exist_ok=True)


@app.route('/health')
def health():
    """Check if service is running"""
    return jsonify({'status': 'ok'})


@app.route('/api/generate', methods=['POST'])
def generate():
    """Generate talking avatar with head pose"""
    data = request.get_json()

    if not data:
        return jsonify({'error': 'No data provided'}), 400

    image_path = data.get('image_path')
    audio_path = data.get('audio_path')
    pose_style = data.get('pose_style', 0)
    expression_scale = data.get('expression_scale', 1.0)
    input_yaw = data.get('input_yaw')
    input_pitch = data.get('input_pitch')
    input_roll = data.get('input_roll')

    if not image_path or not audio_path:
        return jsonify({'error': 'image_path and audio_path are required'}), 400

    if not os.path.exists(image_path):
        return jsonify({'error': f'Image not found: {image_path}'}), 400

    if not os.path.exists(audio_path):
        return jsonify({'error': f'Audio not found: {audio_path}'}), 400

    job_id = uuid.uuid4().hex
    output_path = str(RESULTS_DIR / f"{job_id}_output.mp4")

    cmd = [
        sys.executable, 'inference.py',
        '--driven_audio', audio_path,
        '--source_image', image_path,
        '--result_dir', str(RESULTS_DIR),
        '--checkpoint_dir', str(CHECKPOINTS_DIR),
        '--pose_style', str(pose_style),
        '--expression_scale', str(expression_scale),
        '--size', '256',
        '--preprocess', 'crop',
    ]

    if input_yaw:
        cmd.extend(['--input_yaw'] + [str(x) for x in input_yaw])
    if input_pitch:
        cmd.extend(['--input_pitch'] + [str(x) for x in input_pitch])
    if input_roll:
        cmd.extend(['--input_roll'] + [str(x) for x in input_roll])

    print(f"Running SadTalker: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=str(SADTALKER_DIR))

    if result.returncode != 0:
        return jsonify({
            'error': f'SadTalker failed: {result.stderr}',
            'stdout': result.stdout
        }), 500

    # Find the generated video (SadTalker creates timestamped mp4 files in results dir)
    video_url = None
    for f in RESULTS_DIR.iterdir():
        if f.is_file() and f.suffix == '.mp4' and f.name.startswith('20'):
            shutil.move(str(f), output_path)
            video_url = f'/results/{job_id}_output.mp4'
            break

    if not video_url:
        return jsonify({
            'error': f'SadTalker completed but output not found. Results dir contents: {[f.name for f in RESULTS_DIR.iterdir()]}'
        }), 500

    return jsonify({
        'success': True,
        'job_id': job_id,
        'video_url': video_url
    })


@app.route('/results/<filename>')
def serve_result(filename):
    return send_from_directory(RESULTS_DIR, filename)


if __name__ == '__main__':
    print("Starting SadTalker Service on port 5001...")
    print(f"Checkpoints: {CHECKPOINTS_DIR}")
    app.run(debug=False, host='0.0.0.0', port=5001, threaded=True)
