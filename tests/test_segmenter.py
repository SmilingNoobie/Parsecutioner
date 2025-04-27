from src.segmenter import segment

def test_segment():
    text = 'Experience\nWorked X\nEducation\nBS'
    segs = segment(text)
    assert 'experience' in segs and 'education' in segs