# Backup
---

|                |                                                       |
|----------------|-------------------------------------------------------|
|**Name**        | Backup                                                |
|**Goal**        | Archiving initial dataset                             |
|**Time**        | Few seconds                                                  |
|**Output**      | 00-backup folder                                      |


## Goal

Backup step creates a 00-backup folder where it moves every files, folders submitted to TOAD


## Implementation

### 1- Move files and folders

```
function: shutil.move(image, self.workingDir)
function: shutil.move(folder, self.workingDir)
```




