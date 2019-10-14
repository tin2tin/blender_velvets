# ##### BEGIN GPL LICENSE BLOCK #####
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

# <pep8 compliant>

bl_info = {
    "name": "velvet_revolver ::",
    "description": "Mass-encode proxies and/or transcode to equalize FPSs",
    "author": "szaszak - http://blendervelvets.org",
    "version": (2, 0, 20191009),
    "blender": (2, 80, 0),
    "warning": "Bang! Bang! That awful sound.",
    "category": "Sequencer",
    "location": "File > External Data > Velvet Revolver & Sequencer Preview Header",
    "support": "COMMUNITY"}

import bpy
import os
import glob
import os.path
from bpy.types import Operator
from subprocess import call
from shutil import which
from bpy_extras.io_utils import ExportHelper
from bpy.props import StringProperty, EnumProperty, IntProperty, FloatProperty, BoolProperty

######## ----------------------------------------------------------------------
######## VSE TIMELINE TOGGLE PROXIES <-> FULLRES
######## ----------------------------------------------------------------------


class Proxy_Editing_ToProxy(bpy.types.Operator):
    """Change filepaths of current strips to proxy files (_proxy.mov)"""
    bl_idname = "sequencer.proxy_editing_toproxy"
    bl_label = "Proxy Editing - Change to Proxies"
    bl_options = {'REGISTER', 'UNDO'}
    # Shortcuts: Ctrl + Alt + Shift + P

    @classmethod
    def poll(cls, context):
        if bpy.context.sequences:
            return bpy.context.sequences is not None

    def execute(self, context):

        # Making strips' paths absolute is necessary for script's execution.
        bpy.ops.file.make_paths_absolute()

        def checkProxyFile(f_path, ref):
            ''' Checks for (and returns) correspondent proxy file that may or
            may not have the same extension as the original full_res file '''
            base_path, ext = os.path.splitext(f_path)
            proxy_file = base_path[:ref] + "_proxy" + ext
            # ...and the proxy file has same extension as the fullres
            if os.path.isfile(proxy_file):
                return proxy_file
            # ...or the proxy file has different extension than fullres
            else:
                for e in bpy.path.extensions_movie:
                    proxy_file = base_path[:ref] + "_proxy" + e
                    if os.path.isfile(proxy_file):
                        return proxy_file

        #for s in bpy.context.sequences:
        scene = bpy.context.scene
        for s in scene.sequence_editor.sequences_all:
            if (s.type == "MOVIE"):
                f_path = s.filepath

                # if strip is already a proxy, do nothing
                if "_proxy." in f_path:
                    print("Strip '" + f_path + "' is already a proxy.")
                    pass

                # or strip is a fullres that has correspondent proxy files...
                elif "_PRORES." in f_path:
                    s.filepath = checkProxyFile(f_path, -7)
                    print("Proxy file for '" + f_path + "' is OK.")

                elif "_MJPEG." in f_path:
                    s.filepath = checkProxyFile(f_path, -6)
                    print("Proxy file for '" + f_path + "' is OK.")

                elif "_h264." in f_path:
                    s.filepath = checkProxyFile(f_path, -5)
                    print("Proxy file for '" + f_path + "' is OK.")

                # for fullres files without _PRORES or _MJPEG or _h264 in name
                else:
                    base_path, ext = os.path.splitext(f_path)
                    ext_len = len(ext) + 1
                    # search in folder for any file with the same name appended
                    # by "_proxy" and with recognizeable movie extension
                    if glob.glob(base_path + "_proxy.*") and \
                            ext.lower() in bpy.path.extensions_movie:
                        s.filepath = glob.glob(base_path + "_proxy.*")[0]
                        print("Proxy file for '" + f_path + "' is OK.")
                    else:
                        print("No proxy file found for '" + f_path + "'.")
                        pass

            elif (s.type == "SOUND"):
                # From Blender 2.77 onwards, sound files filepath have to
                # be referred to as s.sound.filepath instead of s.filepath
                f_path = s.sound.filepath

                # if strip is already a proxy, do nothing
                if "_proxy." in f_path:
                    print("Strip '" + f_path + "' is already a proxy.")
                    pass

                # or strip is a fullres that has correspondent proxy files...
                elif "_PRORES." in f_path:
                    s.sound.filepath = checkProxyFile(f_path, -7)
                    print("Proxy file for '" + f_path + "' is OK.")

                elif "_MJPEG." in f_path:
                    s.sound.filepath = checkProxyFile(f_path, -6)
                    print("Proxy file for '" + f_path + "' is OK.")

                elif "_h264." in f_path:
                    s.sound.filepath = checkProxyFile(f_path, -5)
                    print("Proxy file for '" + f_path + "' is OK.")

                # for fullres files without _PRORES or _MJPEG or _h264 in name
                else:
                    base_path, ext = os.path.splitext(f_path)
                    ext_len = len(ext) + 1
                    # search in folder for any file with the same name appended
                    # by "_proxy" and with recognizeable movie extension
                    if glob.glob(base_path + "_proxy.*") and \
                            ext.lower() in bpy.path.extensions_movie:
                        s.sound.filepath = glob.glob(base_path + "_proxy.*")[0]
                        print("Proxy file for '" + f_path + "' is OK.")
                    else:
                        print("No proxy file found for '" + f_path + "'.")
                        pass

        # Make all paths relative; behaviour tends to be standard in Blender
        bpy.ops.file.make_paths_relative()

        return {'FINISHED'}


class Proxy_Editing_ToFullRes(bpy.types.Operator):
    """Change filepaths of current strips back to full-resolution files"""
    bl_idname = "sequencer.proxy_editing_tofullres"
    bl_label = "Proxy Editing - Change to Full Resolution"
    bl_options = {'REGISTER', 'UNDO'}
    # Shortcuts: Ctrl + Shift + P

    @classmethod
    def poll(cls, context):
        if bpy.context.sequences:
            return bpy.context.sequences is not None

    def execute(self, context):

        # Making strips' paths absolute is necessary for script's execution.
        bpy.ops.file.make_paths_absolute()

        #for s in bpy.context.sequences:
        scene = bpy.context.scene
        for s in scene.sequence_editor.sequences_all:
            if (s.type == "MOVIE"):
                f_path = s.filepath

                # if strip is a proxy and has correspondent fullres files
                if "_proxy." in f_path:
                    print("Checking full-res file for '" + f_path + "'...")
                    base_path, ext = os.path.splitext(f_path)
                    f_name = base_path[:-6]

                    if glob.glob(f_name + "_PRORES.*"):
                        s.filepath = glob.glob(f_name + "_PRORES.*")[0]
                        print("Full-res file found.")
                    elif glob.glob(f_name + "_MJPEG.*"):
                        s.filepath = glob.glob(f_name + "_MJPEG.*")[0]
                        print("Full-res file found.")
                    elif glob.glob(f_name + "_h264.*"):
                        s.filepath = glob.glob(f_name + "_h264.*")[0]
                        print("Full-res file found.")
                    elif glob.glob(f_name + ".*"):
                        # if strip's filepath doesn't end with '_MJPEG.mov',
                        # '_PRORES.mov' or '_h264.mov', script will look for
                        # files in folder with the same name as the strip in
                        # the timeline, independent of file's extension
                        # (ie: .mov, .avi etc).
                        s.filepath = glob.glob(f_name + ".*")[0]
                        print("Full-res file found.")
                    else:
                        print("No full-res file found for " + f_name + ".")
                        pass
                else:
                    print("Strip " + f_path + " is not a proxy.")
                    pass

            elif (s.type == "SOUND"):
                # From Blender 2.77 onwards, sound files filepath have to
                # be referred to as s.sound.filepath instead of s.filepath
                f_path = s.sound.filepath

                if "_proxy." in f_path:
                    print("Checking full-res file for '" + f_path + "'...")
                    base_path, ext = os.path.splitext(f_path)
                    f_name = base_path[:-6]

                    if glob.glob(f_name + "_PRORES.*"):
                        s.sound.filepath = glob.glob(f_name + "_PRORES.*")[0]
                        print("Full-res file found.")
                    elif glob.glob(f_name + "_MJPEG.*"):
                        s.sound.filepath = glob.glob(f_name + "_MJPEG.*")[0]
                    elif glob.glob(f_name + "_h264.*"):
                        s.sound.filepath = glob.glob(f_name + "_h264.*")[0]
                        print("Full-res file found.")
                    elif glob.glob(f_name + ".*"):
                        s.sound.filepath = glob.glob(f_name + ".*")[0]
                        print("Full-res file found.")
                    else:
                        print("No full-res file found for " + f_name + ".")
                        pass
                else:
                    print("Strip " + f_path + " is not a proxy.")
                    pass

        # Make all paths relative; behaviour tends to be standard in Blender
        bpy.ops.file.make_paths_relative()

        return {'FINISHED'}


######## ----------------------------------------------------------------------
######## FFMPEG TRANSCODING
######## ----------------------------------------------------------------------

class VideoSource(object):
    """Uses video source to run FFMPEG and encode proxies or full-res intermediates"""
    def __init__(self, ffCommand, filepath, v_source, v_res, v_res_w, v_res_h, v_format,
                 fps, deinter, ar, ac, ow):
        self.ffCommand = ffCommand
        self.input = v_source
        self.filepath = filepath
        self.fps = fps
        self.arate = str(ar)

        self.v_size = "%sx%s" % (v_res_w, v_res_h)

        if deinter:
            self.deinter = " -vf yadif"
        else:
            self.deinter = ""

        if ac:
            self.achannels = " -ac 1"
        else:
            self.achannels = ""

        if ow:
            self.overwrite = " -y"
        else:
            self.overwrite = " -n"

        if v_res == "proxy":
            # Proxy files generated by Velvet Revolver end with "_proxy.mov"
            self.v_output = self.input[:-4] + "_proxy.mov"
            if v_format == "is_prores":
                self.format = "-probesize 5000000 -c:v prores \
                               -profile:v 0 -qscale:v 13 -vendor ap10 \
                               -pix_fmt yuv422p10le -acodec pcm_s16be"
            elif v_format == "is_mjpeg":
                self.format = "-probesize 5000000 -c:v mjpeg \
                               -qscale:v 5 -pix_fmt yuvj422p -acodec pcm_s16be"
            else:  # v_format == "is_h264":
                self.format = "-probesize 5000000 -c:v libx264 -pix_fmt yuv420p \
                               -g 1 -sn -crf 25 -preset ultrafast -tune fastdecode -c:a copy"
                # -preset ultrafast was having problems
                # dealing with ProRes422 from Final Cut
        else: # v_res == "fullres"
            if v_format == "is_prores":
                self.v_output = self.input[:-4] + "_PRORES.mov"
                self.format = "-probesize 5000000 -c:v prores -profile:v 3 \
                               -qscale:v 5 -vendor ap10 -pix_fmt yuv422p10le \
                               -pix_fmt yuvj422p -acodec pcm_s16be"
            elif v_format == "is_mjpeg":
                self.v_output = self.input[:-4] + "_MJPEG.mov"
                self.format = "-probesize 5000000 -c:v mjpeg -qscale:v 1 \
                               -acodec pcm_s16be"
            else: # v_format == "is_h264":
                self.v_output = self.input[:-4] + "_h264.mkv"
                self.format = "-probesize 5000000 -c:v libx264 -pix_fmt yuv420p \
                               -g 1 -sn -crf 25 -preset ultrafast -tune fastdecode -c:a copy"
                # -preset ultrafast was having problems
                # dealing with ProRes422 from Final Cut

    def runFF(self):
        # Due to spaces, the command entries (ffCommand, input and output) have
        # to be read as strings by the call command, thus the escapings below
        callFFMPEG = "\"%s\" -hwaccel auto -i \"%s\" %s -r %s -s %s%s%s -ar %s%s \"%s\"" \
                     % (self.ffCommand, self.input, self.format, self.fps, self.v_size,
                        self.deinter, self.achannels, self.arate, self.overwrite, self.v_output)

        print(callFFMPEG)
        call(callFFMPEG, shell=False)
        if os.path.exists(self.v_output):
            return {'FINISHED'}
        else:
            return {'CANCELED'}


######## ----------------------------------------------------------------------
######## VELVET REVOLVER MAIN CLASS
######## ----------------------------------------------------------------------

class VelvetRevolver(bpy.types.Operator, ExportHelper):
    """Mass encode proxies and/or intra-frame intermediates from original files"""
    bl_idname = "export.revolver"
    bl_label = "Encode Folder"
    filename_ext = "."
    use_filter_folder = True

    transcode_items = (
        ('is_mjpeg', 'MJPEG', ''),
        ('is_prores', 'ProRes422', ''),
        ('is_h264', 'H.264', '')
    )

    proxies: BoolProperty(
        name="Encode Proxies",
        description="Encode proxies with same FPS as current scene",
        default=True,
    )
    prop_proxy_w: IntProperty(
        name="Width",
        description="Proxy videos will have this width",
        default=640
    )
    prop_proxy_h: IntProperty(
        name="Height",
        description="Proxy videos will have this height",
        default=360
    )
    intermediates: BoolProperty(
        name="Encode Intermediates",
        description="Encode intermediates with same FPS as current scene (slow)",
        default=False,
    )
    prop_fullres_w: IntProperty(
        name="Width",
        description="Intermediate videos will have this width",
        default=1920
    )
    prop_fullres_h: IntProperty(
        name="Height",
        description="Intermediate videos will have this height",
        default=1080
    )
    v_format: EnumProperty(
        name="Codec",
        default="is_mjpeg",
        description="Intra-frame format for the creation of proxies and/or intermediates",
        items=transcode_items
    )
    prop_ar: IntProperty(
        name="Audio Sample Rate",
        description="Transcoded videos will have this audio rate",
        default=48000
    )
    prop_deint: BoolProperty(
        name="Deinterlace videos",
        description="Uses FFMPEG Yadif filter to deinterlace all videos",
        default=False,
    )
    prop_ac: BoolProperty(
        name="Force Mono",
        description="Forces FFMPEG to transcode videos to mono - easier panning in Blender, but usually not recommended",
        default=False,
    )
    prop_ow: BoolProperty(
        name="Overwrite",
        description="Allow FFMPEG to overwrite existing files",
        default=False,
    )

    def draw(self, context):

        #fps = context.scene.render.fps
        render = context.scene.render
        fps = round(render.fps / render.fps_base, 2)

        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        box = layout.box()
        box.use_property_split = False
        box.prop(self, 'proxies')
        box.use_property_split = True
        col = box.column(align=True)
        col.active = self.proxies
        col.prop(self, 'prop_proxy_w')
        col.prop(self, 'prop_proxy_h')

        box = layout.box()
        box.use_property_split = False
        box.prop(self, 'intermediates')
        box.use_property_split = True
        col = box.column(align=True)
        col.active = self.intermediates
        col.prop(self, 'prop_fullres_w')
        col.prop(self, 'prop_fullres_h')

        box = layout.box()
        box.prop(self, 'v_format')
        box.prop(self, 'prop_ar')
        box.prop(self, 'prop_deint')
        box.prop(self, 'prop_ac')
        box.prop(self, 'prop_ow')

        col = box.column(align=True)
        col.alignment = 'RIGHT'
        col.label(text="Frame Rate  %.2f fps" % fps)
        col.label(text="(Using Output Properties)")

    @classmethod
    def poll(cls, context):
        if bpy.data.scenes:
            return bpy.data.scenes is not None

    def execute(self, context):
        ffCommand = bpy.context.preferences.addons['velvet_revolver'].preferences.ffCommand

        videosFolderPath, blenderFile = os.path.split(self.filepath)
        videosFolderPath += os.sep

        #fps = context.scene.render.fps
        render = context.scene.render
        fps = round(render.fps / render.fps_base, 2)

        sources = []

        for i in glob.glob(videosFolderPath + "*.*"):
            if i[-4:].lower() in bpy.path.extensions_movie:
                # The line below does not allow for the creation of proxies from
                # a _PRORES or _MJPEG file. TO-DO: creation of sources = [] has
                # to be inside self.proxies and self.intermediates. Then, the script
                # should check for a "original" file (ie. without _prores) ->
                # if it finds it, pass; else, execute ffmpeg command.
                # Also: 'sources' should be sorted by filesize, so that
                # smaller files are transcoded first (create this as an option:
                # sort by filesize, sort by name).
                if "_proxy." not in i and "_MJPEG." not in i \
                   and "_PRORES." not in i and "_h264" not in i:
                    sources.append(i)

        # If nothing is selected to do, abort. Else, continue
        if not self.proxies and not self.intermediates:
            print("No action selected for Velvet Revolver. Aborting.")

        else:
            # Encode a percentage to base a (mouse) progress counter
            wm = bpy.context.window_manager

            if self.proxies and self.intermediates:
                # If Revolver has to encode both proxies and intermediates,
                # there are 2x as many levels to be considered
                inc_level = int(100 / (2 * len(sources)))
            else:
                inc_level = int(100 / len(sources))

            wm.progress_begin(1, 100)
            percentage_level = 1
            wm.progress_update(percentage_level)

            cnt = 0

            if self.proxies:
                for source in sources:
                    v_res = "proxy"
                    vs = VideoSource(ffCommand, videosFolderPath, source, v_res,
                                     self.prop_proxy_w, self.prop_proxy_h,
                                     self.v_format, fps, self.prop_deint,
                                     self.prop_ar, self.prop_ac, self.prop_ow)

                    # Update window_manager progress counter
                    wm.progress_update(percentage_level)
                    percentage_level += inc_level

                    if vs.runFF() == {'CANCELED'}:
                        cnt += 1
                    else:
                        self.report({'INFO'}, "Finished encoding: "+source+" as proxy")

            if self.intermediates:
                for source in sources:
                    v_res = "fullres"
                    vs = VideoSource(ffCommand, videosFolderPath, source, v_res,
                                     self.prop_fullres_w, self.prop_fullres_h,
                                     self.v_format, fps, self.prop_deint,
                                     self.prop_ar, self.prop_ac, self.prop_ow)

                    # Update window_manager progress counter
                    wm.progress_update(percentage_level)
                    percentage_level += inc_level

                    if vs.runFF() == {'CANCELED'}:
                        cnt += 1

            # Finish report on progress counter
            wm.progress_end()

            if cnt != 0:
                print("Some files where not encoded. Look above for more info.")
                # self.report({'ERROR'}, "Some files where not encoded. Look in the System Console for more info.")
            else:
                self.report({'INFO'}, "Velvet Revolver finished encoding files.")

        return {'FINISHED'}


class Velvet_Revolver_Transcoder(bpy.types.AddonPreferences):
    """Velver Revolver preferences"""
    bl_idname = __name__.split(".")[0]
    bl_option = {'REGISTER'}

    if which('ffmpeg') is not None:
        ffmpeg = which('ffmpeg')
    else:
        ffmpeg = "/usr/bin/ffmpeg"

    ffCommand: StringProperty(
        name="Path to FFMPEG binary or executable",
        description="If you have a local FFMPEG, change this path",
        subtype='FILE_PATH',
        default=ffmpeg,
    )

    def draw(self, context):

        layout = self.layout
        layout.label(text="The path below *must* be absolute. If you have to "
                          "change it, do so with no .blend files open or "
                          "they will be relative.")
        layout.prop(self, "ffCommand")


def menuEntry(self, context):
    self.layout.operator(VelvetRevolver.bl_idname, text="Velvet Revolver")


class SEQUENCER_OT_proxy_swap(bpy.types.Operator):
    """Swap to and from Proxy Files"""
    bl_idname = "sequencer.revolver"
    bl_label = "Proxy Swap"
    bl_options = {"REGISTER", "UNDO"}

    type: bpy.props.EnumProperty(
        name="Proxy Swap",
        description="Proxy Swap",
        options={'ENUM_FLAG'},
        items=(
             ('INTERMEDIATES', "Intermediates", "Swap to intermediate files"),
             ('PROXY', "Proxies", "Swap to proxy files"),
             ),
             default={'INTERMEDIATES'},
        )


    @classmethod
    def poll(cls, context):
        if context.sequences:
            return True
        return False


    def execute(self, context):
        if self.type == {'PROXY'}:
            bpy.ops.sequencer.proxy_editing_toproxy()
        else:
            bpy.ops.sequencer.proxy_editing_tofullres()

        scene = bpy.context.scene
        for s in scene.sequence_editor.sequences_all:
            if (s.type == "MOVIE"):
                strip = s

                # hack: update in viewport to read source img orig_width and orig_height
                # switch view and area
                oldf = scene.frame_current
                area = bpy.context.area
                original_type = area.type
                area.type = 'SEQUENCE_EDITOR'
                original_view = area.spaces[0].view_type
                area.spaces[0].view_type = 'PREVIEW'
                # NOTE playhead steps alone are sufficient when user has visible VSE Preview
                frame_initial = scene.frame_current
                scene.frame_current = strip.frame_start
                bpy.ops.render.opengl(sequencer=True)

                # gather image data
                img = strip.elements[0]
                # store dimensions

                if not (img.orig_width and img.orig_height):
                    print("pretty_img - Failed to rescale img with width or height of 0: {0}".format(img.filename))
                    return

                img_res = {
                    'w': img.orig_width,
                    'h': img.orig_height
                }
                print("%s: %s" % (img.filename, "{0} x {1}".format(img_res['w'], img_res['h'])))
                bpy.context.scene.render.resolution_x = img_res['w']
                bpy.context.scene.render.resolution_y = img_res['h']

                bpy.ops.sequencer.view_all_preview() # doesn't work

                # reset view and area
                area.spaces[0].view_type = original_view
                area.type = original_type
                # /hack

                scene.frame_current = oldf
                break

        return {'FINISHED'}


def headerEntry(self, context):
    layout = self.layout
    st = context.space_data
    if st.view_type in {'PREVIEW', 'SEQUENCER_PREVIEW'}:
        layout.operator_menu_enum("sequencer.revolver", "type")


classes = (
    Proxy_Editing_ToProxy,
    Proxy_Editing_ToFullRes,
#    VideoSource,
    VelvetRevolver,
    Velvet_Revolver_Transcoder,
    SEQUENCER_OT_proxy_swap,
)

# store keymaps here to access after registration
revolver_keymaps = []

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    # Add menu entry
    bpy.types.TOPBAR_MT_file_external_data.append(menuEntry)
    # Add header entry
    bpy.types.SEQUENCER_HT_header.append(headerEntry)

    # Handle the keymap for Proxy_Editing
    wm = bpy.context.window_manager
    km = wm.keyconfigs.addon.keymaps.new(name = "Sequencer", space_type='SEQUENCE_EDITOR', region_type='WINDOW')

    kmi = km.keymap_items.new(Proxy_Editing_ToFullRes.bl_idname, 'P', 'PRESS', shift=True, ctrl=True)
    revolver_keymaps.append((km, kmi))

    kmi = km.keymap_items.new(Proxy_Editing_ToProxy.bl_idname, 'P', 'PRESS', shift=True, ctrl=True, alt=True)
    revolver_keymaps.append((km, kmi))


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    # Remove menu entry
    bpy.types.TOPBAR_MT_file_external_data.remove(menuEntry)
    # Remove menu entry
    bpy.types.SEQUENCER_HT_header.remove(headerEntry)

    # Unregister Proxy_Editing shortcut
    for km, kmi in revolver_keymaps:
        km.keymap_items.remove(kmi)
    revolver_keymaps.clear()


if __name__ == "__main__":
    register()
