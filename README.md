# VokVision

## Data Flow

```mermaid
sequenceDiagram
    participant U as User
    participant M as Mobile App
    participant B as Backend
    participant P as Processing Engine

    U->>M: Capture Photos
    M->>B: Upload Images
    B->>P: Start Reconstruction Job
    P-->>B: Mesh Generated
    B-->>M: Notify Completion
    M->>U: Preview 3D Model
    U->>M: Edit Model (Resize/Reshape)
    M->>B: Request Modification
    B->>P: Apply AI Transform
    P-->>B: Updated Mesh
    B-->>M: Return New Model
```

## Directory Structure

```plaintext
root/
├── lib/                        # Flutter Mobile App
│   ├── main.dart
│   └── src/
│       ├── features/           # Domain Modules
│       │   ├── authentication/
│       │   ├── capture/
│       │   ├── reconstruction/
│       │   ├── editor/
│       │   └── gallery/
│       └── shared/             # Common Utilities
└── backend/                    # Python Server
    └── src/
        ├── api/                # API Routes
        └── features/           # Domain Logic
            ├── ingestion/
            ├── processing/
            ├── ai_editor/
            └── storage/
```
