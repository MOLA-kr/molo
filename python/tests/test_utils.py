from unittest import TestCase

import gazu.project

from molo.auth import Auth
from molo.utils import construct_full_path


# 신유
class Test(TestCase):
    def setUp(self) -> None:
        self.auth = Auth()
        self.auth.connect_host('http://192.168.3.116/api')
        self.auth.log_in('pipeline@rapa.org', 'netflixacademy')

    def tearDown(self) -> None:
        self.auth.log_out()

    def test_construct_full_path(self):
        camera_file = gazu.files.get_output_file('d888b823-98c9-4ca6-bd93-ce5903b3807e')
        rendering_file = gazu.files.get_output_file('ca62c91d-a59d-4e79-b9dd-43e074bb8b77')
        camera_path = "/mnt/pipeline/personal/minjichoi/kitsu/test_proj/shots/sq03/sh01/camera/output/002" \
                      "/test_proj_sq03_sh01_camera_002.fbx"
        rendering_path = "/mnt/pipeline/personal/minjichoi/kitsu/test_proj/shots/sq03/sh01/rendering/output/014" \
                         "/test_proj_sq03_sh01_rendering_014.####.exr"
        no_padding_path = "/mnt/pipeline/personal/minjichoi/kitsu/test_proj/shots/sq03/sh01/rendering/output/014" \
                          "/test_proj_sq03_sh01_rendering_014.exr"
        self.assertEqual(construct_full_path(camera_file), camera_path)
        self.assertEqual(construct_full_path(rendering_file), rendering_path)
        self.assertNotEqual(construct_full_path(rendering_file), no_padding_path)
        # self.assertEqual(self.auth.valid_host, True)
        # self.assertEqual(self.auth.valid_user, True)
