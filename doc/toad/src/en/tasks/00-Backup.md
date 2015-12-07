# Backup
---

|                |                                                       |
|----------------|-------------------------------------------------------|
|**Name**        | Backup                                                |
|**Goal**        | Archiving initial dataset                             |
|**Time**        | Few seconds                                           |
|**Output**      | 00-backup folder                                      |

#

## Goal

The backup step creates a 00-backup folder into which it moves every file and folder submitted to TOAD


## Implementation

### 1- Move files and folders

```
function: shutil.move(image, self.workingDir)
function: shutil.move(folder, self.workingDir)
```

