bl_info = {
    "name": "Cube Grid Generator",
    "author": "Simran Pundir",
    "version": (1, 0),
    "blender": (3, 0, 0),
    "location": "View3D > Sidebar > Task 2",
    "description": "Generate and manage cube grids in the 3D viewport",
    "category": "Object",
}
from mathutils import Vector
import bpy
from bpy.types import Panel
from bpy.props import IntProperty

class TASK2_OT_CreateCubes(bpy.types.Operator):
    bl_idname = "task2.create_cubes"
    bl_label = "Create Cube Grid"

    def execute(self, context):
        import math

        n = context.scene.cube_count
        if n > 20:
            self.report({'ERROR'}, "The number is out of range")
            return {'CANCELLED'}

        collection_name = "GeneratedCubes"
        if collection_name in bpy.data.collections:
            cube_collection = bpy.data.collections[collection_name]
        else:
            cube_collection = bpy.data.collections.new(collection_name)
            context.scene.collection.children.link(cube_collection)
        for obj in list(cube_collection.objects):
            bpy.data.objects.remove(obj, do_unlink=True)
            
        layer_collection = context.view_layer.layer_collection
        
        def find_layer_collection(layer_col, name):
            if layer_col.collection.name == name:
               return layer_col
            for child in layer_col.children:
                found = find_layer_collection(child, name)
                if found:
                    return found
            return None
        generated_layer = find_layer_collection(layer_collection, "GeneratedCubes")
        context.view_layer.active_layer_collection = generated_layer

        spacing = 1.0
        m = math.ceil(math.sqrt(n))
        rows = math.ceil(n / m)

        count = 0
        for row in range(rows):
            for col in range(m):
                if count >= n:
                   break
                x = col * spacing
                y = row * spacing
                z = 0

                bpy.ops.mesh.primitive_cube_add(size=1, location=(x, y, z))
                count += 1

        self.report({'INFO'}, f"Created {n} cubes")
        return {'FINISHED'}
class TASK2_OT_DeleteSelected(bpy.types.Operator):
    bl_idname = "task2.delete_selected"
    bl_label = "Delete Selected Cubes"

    def execute(self, context):
        deleted = False

        for obj in context.selected_objects:
            if obj.type == 'MESH':
                bpy.data.objects.remove(obj, do_unlink=True)
                deleted = True

        if not deleted:
            self.report({'WARNING'}, "No mesh objects selected")
            return {'CANCELLED'}

        self.report({'INFO'}, "Selected cubes deleted")
        return {'FINISHED'}

class TASK2_OT_MergeSelected(bpy.types.Operator):
    bl_idname = "task2.merge_selected"
    bl_label = "Merge Selected Meshes"

    def execute(self, context):
        selected = [obj for obj in context.selected_objects if obj.type == 'MESH']

        if len(selected) < 2:
            self.report({'ERROR'}, "Select at least two mesh objects")
            return {'CANCELLED'}

        if not self.have_common_face(selected):
            self.report(
               {'WARNING'},
               "Common face could not be reliably detected; merging anyway"
            )
        bpy.ops.object.join()
        self.report({'INFO'}, "Meshes merged")
        return {'FINISHED'}

    def have_common_face(self, objects):
        bboxes = [obj.bound_box for obj in objects]

        def world_bbox(obj):
            return [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]

        world_boxes = [world_bbox(obj) for obj in objects]

        base = world_boxes[0]

        for other in world_boxes[1:]:
            if self.boxes_touch(base, other):
                return True

        return False

    def boxes_touch(self, box1, box2, eps=0.01):
        def min_max(box, axis):
            values = [getattr(v, axis) for v in box]
            return min(values), max(values)

        for axis in ['x', 'y', 'z']:
            min1, max1 = min_max(box1, axis)
            min2, max2 = min_max(box2, axis)
            if abs(max1 - min2) < eps or abs(max2 - min1) < eps:
                other_axes = [a for a in ['x', 'y', 'z'] if a != axis]
                overlap = True
                
                for oa in other_axes:
                    o1_min, o1_max = min_max(box1, oa)
                    o2_min, o2_max = min_max(box2, oa)
                    if o1_max < o2_min or o2_max < o1_min:
                        overlap = False

                if overlap:
                   return True

        return False


class TASK2_PT_CubePanel(Panel):
    bl_label = "Task 2: Cube Tools"
    bl_idname = "TASK2_PT_cube_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Task 2"

    def draw(self, context):
        layout = self.layout
        layout.label(text="Cube Grid Generator")
        layout.prop(context.scene, "cube_count")
        layout.operator("task2.create_cubes")
        layout.operator("task2.delete_selected")
        layout.operator("task2.merge_selected")


def register():
    bpy.utils.register_class(TASK2_OT_CreateCubes)
    bpy.utils.register_class(TASK2_OT_DeleteSelected)
    bpy.utils.register_class(TASK2_PT_CubePanel)
    bpy.utils.register_class(TASK2_OT_MergeSelected)


    bpy.types.Scene.cube_count = IntProperty(
        name="Number of Cubes",
        description="Enter a natural number (<20)",
        default=1,
        min=1
    )


def unregister():
    del bpy.types.Scene.cube_count
    bpy.utils.unregister_class(TASK2_PT_CubePanel)
    bpy.utils.unregister_class(TASK2_OT_DeleteSelected)
    bpy.utils.unregister_class(TASK2_OT_CreateCubes)
    bpy.utils.unregister_class(TASK2_OT_MergeSelected)


if __name__ == "__main__":
    register()
