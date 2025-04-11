import os

# Folder where your training labels are
label_folder = "atraining/train/labels"

# Class remapping: old_label → new_label
remap = {
    0: 1,
    1: 0,
    2: 2
}

for file in os.listdir(label_folder):
    if file.endswith(".txt"):
        path = os.path.join(label_folder, file)
        with open(path, "r") as f:
            lines = f.readlines()

        new_lines = []
        for line in lines:
            parts = line.strip().split()
            if not parts:
                continue
            cls_id = int(parts[0])
            new_cls = remap.get(cls_id, cls_id)
            parts[0] = str(new_cls)
            new_lines.append(" ".join(parts))

        with open(path, "w") as f:
            f.write("\n".join(new_lines))
