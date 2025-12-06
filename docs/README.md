# Reachy Mini App Suite - Documentation

Welcome to the Reachy Mini App Suite documentation. This suite provides multiple applications for controlling and interacting with the Reachy Mini robot.

---

## 📁 Documentation Structure

```
docs/
├── README.md                          # This file - documentation index
├── getting-started.md                 # Quick start guide for developers
├── assistant-instructions.md          # AI assistant context and guidelines
│
├── reachy-remix/                      # 🎵 Reachy Remix Motion Builder (ACTIVE)
│   ├── PRD.md                         # Product Requirements Document
│   ├── reachy-remix-architecture.md   # Technical architecture
│   ├── reachy-remix-stories.md        # User stories & sprint plan
│   └── PROGRESS.md                    # Sprint progress tracking (LIVE)
│
├── other-apps/                        # Other applications in the suite
│   ├── music-reactive-app.md          # Music-reactive dance app
│   └── musical-notes-feature.md       # Musical note generation feature
│
├── reference/                         # Technical reference materials
│   ├── api-reference.md               # API documentation
│   └── daemon-setup.md                # Reachy daemon setup guide
│
├── sprint-artifacts/                  # Sprint planning & tracking
│   ├── sdk-integration-plan.md        # SDK integration strategy
│   └── workflow-init-summary.md       # Workflow initialization
│
└── archive/                           # Historical/deprecated docs
    └── pre-prd.reachy-app-suite.md    # Original app suite concept
```

---

## 🚀 Current Focus: Reachy Remix

**Reachy Remix** is a Scratch-lite motion builder that lets kids create dance sequences using tap-to-add blocks.

**Key Documents:**
- **[PRD](./reachy-remix/PRD.md)** - What we're building and why
- **[Architecture](./reachy-remix/reachy-remix-architecture.md)** - How we're building it
- **[Stories](./reachy-remix/reachy-remix-stories.md)** - Sprint plan and implementation tasks
- **[Progress](./reachy-remix/PROGRESS.md)** - Live sprint tracking 🔥

**Current Sprint:** Sprint 1 (Dec 6-12, 2025)  
**Status:** 🚀 In progress - Story 1 complete ✅ (3/21 points, 14%)

---

## 📖 Quick Links

### For Developers
- **[Getting Started Guide](./getting-started.md)** - Setup and first steps
- **[API Reference](./reference/api-reference.md)** - Complete API documentation
- **[Daemon Setup](./reference/daemon-setup.md)** - Configure Reachy connection

### For Project Management
- **[Reachy Remix Stories](./reachy-remix/reachy-remix-stories.md)** - Current sprint tasks
- **[Sprint Artifacts](./sprint-artifacts/)** - Planning documents

### For AI Assistants
- **[Assistant Instructions](./assistant-instructions.md)** - Context and guidelines

---

## 🏗️ Project Architecture

The suite is built on common infrastructure:

```
src/
├── common/
│   ├── reachy/          # Robot control wrappers
│   │   ├── robot_wrapper.py       # High-level robot interface
│   │   ├── safe_motions.py        # Pre-validated gestures
│   │   └── ...
│   ├── core/            # Shared utilities
│   └── ui/              # Common UI components
│
└── apps/
    ├── reachy-remix/    # Motion builder app (CURRENT)
    ├── music-reactive/  # Music dance app
    └── ...
```

---

## 🎯 Development Workflow

### Current Sprint (Reachy Remix MVP)

1. **Story 1** - Gradio UI shell + theme (3 pts)
2. **Story 2** - Motion Engine + SDK integration (5 pts)
3. **Story 3** - State management + sequence builder (5 pts)
4. **Story 4** - Play execution + status feedback (5 pts)
5. **Story 5** - Visual polish + animations (3 pts)

**Total:** 21 points over 5 days

See [reachy-remix-stories.md](./reachy-remix/reachy-remix-stories.md) for details.

---

## 📝 Documentation Standards

When creating or updating documentation:

1. **Use CommonMark** - Standard Markdown syntax
2. **Include examples** - Show, don't just tell
3. **Keep it current** - Update docs with code changes
4. **Link extensively** - Connect related documents
5. **Add diagrams** - Use Mermaid for architecture/flows

### File Naming
- Use kebab-case: `reachy-remix-stories.md`
- Be descriptive: `api-reference.md` not `api.md`
- Date sprint artifacts: `sprint-1-retro-2025-12-12.md`

---

## 🤝 Contributing

When adding new features or apps:

1. Create a folder in `docs/` for your app/feature
2. Start with a PRD (Product Requirements Document)
3. Add architecture document if complex
4. Break into user stories
5. Update this README with links

---

## 📚 Additional Resources

- **[Reachy Mini SDK Docs](https://docs.pollen-robotics.com/)** - Official SDK documentation
- **[Gradio Documentation](https://www.gradio.app/docs/)** - UI framework docs
- **[Project Repository](https://github.com/chelleboyer/reachy_mini_app_suite)** - Source code

---

## 📅 Document History

| Date | Change | Author |
|------|--------|--------|
| 2025-12-06 | Documentation reorganization, added structure | Paige (Tech Writer) |
| 2025-12-06 | Reachy Remix PRD, Architecture, Stories added | Team (Party Mode) |
| 2025-11-XX | Initial documentation created | Various |

---

**Last Updated:** December 6, 2025  
**Maintained By:** Documentation Team  
**Questions?** See [assistant-instructions.md](./assistant-instructions.md) for AI assistant context
