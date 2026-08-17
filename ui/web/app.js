/* ==========================================================================
   CAPTAIN AI OS — J.A.R.V.I.S. SCI-FI HUD RUNTIME ENGINE
   DIRECT VOICE-TO-TEXT & TEXT-TO-VOICE SYSTEM WITH BACKEND GRAPH INTEGRATION
   ========================================================================== */

class CaptainCoreEngine {
    constructor() {
        this.ENGINE_STATES = {
            IDLE: 'IDLE',
            ATTENTION: 'ATTENTION',
            LISTENING: 'LISTENING',
            UNDERSTANDING: 'UNDERSTANDING',
            THINKING: 'THINKING',
            EXECUTING: 'EXECUTING',
            RESPONDING: 'RESPONDING',
            WAITING: 'WAITING',
            NOTIFICATION: 'NOTIFICATION',
            RECOVERY: 'RECOVERY'
        };

        this.LAYERS = {
            LAYER_1: 'layer-1-neural-core',
            LAYER_2: 'layer-2-energy-shell',
            LAYER_3: 'layer-3-orbital-structure',
            LAYER_4: 'layer-4-ambient-field',
            LAYER_5: 'layer-5-communication',
            LAYER_6: 'layer-6-intelligence',
            LAYER_7: 'layer-7-interaction',
            LAYER_8: 'layer-8-environmental'
        };

        this.STATE_PRIORITIES = {
            RECOVERY: 10,
            NOTIFICATION: 9,
            RESPONDING: 8,
            EXECUTING: 7,
            THINKING: 6,
            UNDERSTANDING: 5,
            LISTENING: 4,
            ATTENTION: 3,
            WAITING: 2,
            IDLE: 1
        };

        this.COMMUNICATION_PHASES = {
            USER_SPEAKING_START: 'USER_SPEAKING_START',
            USER_SPEAKING_ACTIVE: 'USER_SPEAKING_ACTIVE',
            USER_PAUSE: 'USER_PAUSE',
            USER_SPEAKING_END: 'USER_SPEAKING_END',
            CAPTAIN_RESPONDING_START: 'CAPTAIN_RESPONDING_START',
            CAPTAIN_RESPONDING_ACTIVE: 'CAPTAIN_RESPONDING_ACTIVE',
            CAPTAIN_RESPONDING_END: 'CAPTAIN_RESPONDING_END'
        };

        this.SPATIAL_ZONES = {
            ZONE_1_CENTRAL_PRESENCE: 'zone-central-presence',
            ZONE_2_NAVIGATION: 'zone-navigation',
            ZONE_3_MEMORY_STREAM: 'zone-memory',
            ZONE_4_INTELLIGENCE_STREAM: 'zone-intelligence',
            ZONE_5_WORKSPACE: 'zone-workspace',
            ZONE_6_UTILITY: 'zone-utility'
        };

        this.WORKSPACE_MODES = {
            CONVERSATION: 'CONVERSATION',
            CODING: 'CODING',
            RESEARCH: 'RESEARCH',
            KNOWLEDGE: 'KNOWLEDGE',
            AUTOMATION: 'AUTOMATION',
            FILES: 'FILES',
            SYSTEM: 'SYSTEM',
            CREATIVE: 'CREATIVE'
        };

        this.NAV_PANE_SECTIONS = {
            CONVERSATIONS: 'CONVERSATIONS',
            PROJECTS: 'PROJECTS',
            MEMORIES: 'MEMORIES',
            KNOWLEDGE_GRAPH: 'KNOWLEDGE_GRAPH',
            FILES: 'FILES',
            AGENTS: 'AGENTS',
            WORKFLOWS: 'WORKFLOWS'
        };

        this.DOCK_LAUNCHER_ACTIONS = {
            VOICE_INPUT: 'VOICE_INPUT',
            CHAT_INTERFACE: 'CHAT_INTERFACE',
            SEARCH_PALETTE: 'SEARCH_PALETTE',
            TERMINAL: 'TERMINAL',
            FILE_EXPLORER: 'FILE_EXPLORER',
            SYSTEM_SETTINGS: 'SYSTEM_SETTINGS'
        };

        this.MEMORY_CENTER_VIEWS = {
            SHORT_TERM_SESSION: 'SHORT_TERM_SESSION',
            LONG_TERM_SEMANTIC: 'LONG_TERM_SEMANTIC',
            ENTITY_RELATIONSHIP_GRAPH: 'ENTITY_RELATIONSHIP_GRAPH',
            CONTEXTUAL_INDEX: 'CONTEXTUAL_INDEX'
        };

        this.REASONING_STAGES = {
            UNDERSTANDING: 'UNDERSTANDING',
            PLANNING: 'PLANNING',
            GATHERING_INFORMATION: 'GATHERING_INFORMATION',
            PROCESSING: 'PROCESSING',
            VERIFYING: 'VERIFYING',
            RESPONDING: 'RESPONDING'
        };

        this.SUBAGENTS = {
            CONVERSATION_AGENT: 'CONVERSATION_AGENT',
            CODING_AGENT: 'CODING_AGENT',
            SYSTEM_AGENT: 'SYSTEM_AGENT',
            RAG_AGENT: 'RAG_AGENT',
            SEARCH_AGENT: 'SEARCH_AGENT',
            COMMS_AGENT: 'COMMS_AGENT'
        };

        this.AWARENESS_CATEGORIES = {
            CAPTAIN_STATUS: 'CAPTAIN_STATUS',
            AI_RUNTIME: 'AI_RUNTIME',
            DEVICE_RESOURCES: 'DEVICE_RESOURCES',
            CONNECTIVITY: 'CONNECTIVITY',
            SENSORS: 'SENSORS',
            BACKGROUND_SERVICES: 'BACKGROUND_SERVICES'
        };

        this.PERCEPTION_CATEGORIES = {
            VOICE_PERCEPTION: 'VOICE_PERCEPTION',
            FACE_AWARENESS: 'FACE_AWARENESS',
            GESTURE_AWARENESS: 'GESTURE_AWARENESS',
            PRESENCE_AWARENESS: 'PRESENCE_AWARENESS',
            ATTENTION_AWARENESS: 'ATTENTION_AWARENESS'
        };

        this.VOICE_FEEDBACK_STATES = {
            IDLE: 'IDLE',
            LISTENING: 'LISTENING',
            PROCESSING: 'PROCESSING',
            SPEAKING: 'SPEAKING',
            INTERRUPTED: 'INTERRUPTED',
            UNAVAILABLE: 'UNAVAILABLE'
        };

        this.INTERACTION_MODALITIES = {
            VOICE: 'VOICE',
            TEXT: 'TEXT',
            TOUCH: 'TOUCH',
            MOUSE_POINTER: 'MOUSE_POINTER',
            KEYBOARD: 'KEYBOARD'
        };

        this.MOTION_DESIGN_PRINCIPLES = {
            INTENTIONALITY: 'INTENTIONALITY',
            SPATIAL_CONTINUITY: 'SPATIAL_CONTINUITY',
            STATE_AWARENESS: 'STATE_AWARENESS',
            RESPONSIVENESS: 'RESPONSIVENESS',
            HIERARCHICAL_DECAY: 'HIERARCHICAL_DECAY'
        };

        this.INTERACTION_ANIMATIONS = {
            HOVER_FEEDBACK: 'HOVER_FEEDBACK',
            PRESS_FEEDBACK: 'PRESS_FEEDBACK',
            SELECTION_FEEDBACK: 'SELECTION_FEEDBACK',
            FOCUS_RING_GLOW: 'FOCUS_RING_GLOW'
        };

        this.ENVIRONMENTAL_EFFECTS = {
            LIGHTING_PROFILES: 'LIGHTING_PROFILES',
            PARTICLE_FIELDS: 'PARTICLE_FIELDS',
            BLUR_DEPTH: 'BLUR_DEPTH',
            DEPTH_PARALLAX: 'DEPTH_PARALLAX'
        };

        this.QUALITY_PROFILES = {
            HIGH: 'HIGH',
            BALANCED: 'BALANCED',
            LOW_POWER: 'LOW_POWER'
        };

        this.UNIFIED_DESIGN_SUBSYSTEMS = {
            LAYOUT_SYSTEM: 'LAYOUT_SYSTEM',
            COLOR_SYSTEM: 'COLOR_SYSTEM',
            TYPOGRAPHY_SYSTEM: 'TYPOGRAPHY_SYSTEM',
            COMPONENT_SYSTEM: 'COMPONENT_SYSTEM',
            MOTION_SYSTEM: 'MOTION_SYSTEM',
            SPATIAL_SYSTEM: 'SPATIAL_SYSTEM',
            VISUAL_LANGUAGE: 'VISUAL_LANGUAGE',
            ACCESSIBILITY_SYSTEM: 'ACCESSIBILITY_SYSTEM'
        };

        this.SPATIAL_LAYOUT_ZONES = {
            CAPTAIN_ZONE: 'CAPTAIN_ZONE',
            NAVIGATION_ZONE: 'NAVIGATION_ZONE',
            WORKSPACE_ZONE: 'WORKSPACE_ZONE',
            INFORMATION_ZONE: 'INFORMATION_ZONE',
            UTILITY_ZONE: 'UTILITY_ZONE'
        };

        this.UNIFIED_VISUAL_HIERARCHY = {
            LEVEL_1: 'CAPTAIN_CORE',
            LEVEL_2: 'ACTIVE_WORKSPACE',
            LEVEL_3: 'USER_INTERACTION',
            LEVEL_4: 'PRIMARY_INFORMATION',
            LEVEL_5: 'SUPPORTING_INFORMATION',
            LEVEL_6: 'UTILITIES',
            LEVEL_7: 'ENVIRONMENTAL_EFFECTS'
        };

        this.COMPONENT_DESIGN_CATEGORIES = {
            NAVIGATION_COMPONENTS: 'NAVIGATION_COMPONENTS',
            INPUT_COMPONENTS: 'INPUT_COMPONENTS',
            DISPLAY_COMPONENTS: 'DISPLAY_COMPONENTS',
            WORKSPACE_COMPONENTS: 'WORKSPACE_COMPONENTS',
            FEEDBACK_COMPONENTS: 'FEEDBACK_COMPONENTS',
            OVERLAY_COMPONENTS: 'OVERLAY_COMPONENTS',
            UTILITY_COMPONENTS: 'UTILITY_COMPONENTS'
        };

        this.WORKSPACE_PANELS = { PRIMARY_WORKSPACE: 'PRIMARY_WORKSPACE', CONTEXTUAL_SIDEBAR: 'CONTEXTUAL_SIDEBAR', FLOATING_WINDOWS: 'FLOATING_WINDOWS', UTILITY_DOCK: 'UTILITY_DOCK' };
        this.WINDOW_PANELS = { CONVERSATION_STREAM: 'CONVERSATION_STREAM', CODE_EDITOR: 'CODE_EDITOR', RESEARCH_STREAM: 'RESEARCH_STREAM', MEMORY_INSPECTOR: 'MEMORY_INSPECTOR', SYSTEM_TELEMETRY: 'SYSTEM_TELEMETRY' };
        this.NOTIFICATION_ALERTS = { SYSTEM_ALERT: 'SYSTEM_ALERT', PROACTIVE_SUGGESTION: 'PROACTIVE_SUGGESTION', CONTEXT_REMINDER: 'CONTEXT_REMINDER' };
        this.INTERFACE_STATES = { DEFAULT: 'DEFAULT', FOCUSED: 'FOCUSED', COMPLIANT: 'COMPLIANT' };

        this.MEMORY_TIMELINE = { ACTIVE_THREAD: 'ACTIVE_THREAD', RECENT_TURNS: 'RECENT_TURNS', HISTORICAL_SESSIONS: 'HISTORICAL_SESSIONS' };
        this.MEMORY_SEARCH = { SEMANTIC_SEARCH: 'SEMANTIC_SEARCH', KEYWORD_FILTER: 'KEYWORD_FILTER', CATEGORY_FILTER: 'CATEGORY_FILTER' };
        this.MEMORY_GRAPH = { ENTITY_NODES: 'ENTITY_NODES', RELATIONSHIP_EDGES: 'RELATIONSHIP_EDGES', CLUSTER_GROUPS: 'CLUSTER_GROUPS' };
        this.MEMORY_VISUALIZATIONS = { TIMELINE_VIEW: 'TIMELINE_VIEW', GRAPH_VIEW: 'GRAPH_VIEW', STREAM_VIEW: 'STREAM_VIEW' };
        this.MEMORY_WORKSPACE_INTEGRATION = { CONTEXT_INJECTION: 'CONTEXT_INJECTION', MEMORY_RETRIEVAL: 'MEMORY_RETRIEVAL', MEMORY_PERSISTENCE: 'MEMORY_PERSISTENCE' };

        this.INTELLIGENCE_CENTER = { AGENT_SWARM: 'AGENT_SWARM', REASONING_TIMELINE: 'REASONING_TIMELINE', TASK_PIPELINE: 'TASK_PIPELINE' };
        this.MULTI_AGENT_SWARM = { CONVERSATION_AGENT: 'CONVERSATION_AGENT', CODING_AGENT: 'CODING_AGENT', SYSTEM_AGENT: 'SYSTEM_AGENT', RAG_AGENT: 'RAG_AGENT', SEARCH_AGENT: 'SEARCH_AGENT', COMMS_AGENT: 'COMMS_AGENT' };
        this.TASK_EXECUTION_VISUALIZATION = { TASK_QUEUE: 'TASK_QUEUE', EXECUTION_GRAPH: 'EXECUTION_GRAPH', OUTPUT_AGGREGATOR: 'OUTPUT_AGGREGATOR' };
        this.SYSTEM_AWARENESS_DASHBOARD = { CAPTAIN_STATUS: 'CAPTAIN_STATUS', AI_RUNTIME: 'AI_RUNTIME', DEVICE_RESOURCES: 'DEVICE_RESOURCES', CONNECTIVITY: 'CONNECTIVITY', SENSORS: 'SENSORS', BACKGROUND_SERVICES: 'BACKGROUND_SERVICES' };
        this.HUMAN_PERCEPTION_VISUALIZATION = { VOICE_PERCEPTION: 'VOICE_PERCEPTION', FACE_AWARENESS: 'FACE_AWARENESS', GESTURE_AWARENESS: 'GESTURE_AWARENESS', PRESENCE_AWARENESS: 'PRESENCE_AWARENESS', ATTENTION_AWARENESS: 'ATTENTION_AWARENESS' };
        this.INTELLIGENCE_EVENT_STREAM = { REASONING_EVENTS: 'REASONING_EVENTS', DELEGATION_EVENTS: 'DELEGATION_EVENTS', PROACTIVE_EVENTS: 'PROACTIVE_EVENTS', SYSTEM_EVENTS: 'SYSTEM_EVENTS' };

        this.VOICE_EXPERIENCE = { VOICE_STT: 'VOICE_STT', VOICE_TTS: 'VOICE_TTS', VOICE_VISUALIZER: 'VOICE_VISUALIZER' };
        this.VOICE_STATE_FEEDBACK = { IDLE: 'IDLE', LISTENING: 'LISTENING', PROCESSING: 'PROCESSING', SPEAKING: 'SPEAKING', INTERRUPTED: 'INTERRUPTED', UNAVAILABLE: 'UNAVAILABLE' };
        this.CONVERSATION_FLOW = { TURN_TAKING: 'TURN_TAKING', STREAMING_RESPONSE: 'STREAMING_RESPONSE', CONVERSATION_RECOVERY: 'CONVERSATION_RECOVERY' };
        this.PROACTIVE_INTERACTION = { PROACTIVE_SUGGESTIONS: 'PROACTIVE_SUGGESTIONS', CONTEXT_NOTIFICATIONS: 'CONTEXT_NOTIFICATIONS', ASSISTIVE_ALERTS: 'ASSISTIVE_ALERTS' };
        this.VOICE_PERSONALITY = { CAPTAIN_TONE: 'CAPTAIN_TONE', SPEECH_RATE: 'SPEECH_RATE', PITCH_CONTOUR: 'PITCH_CONTOUR' };
        this.MULTIMODAL_INTERACTION = { VOICE_MODALITY: 'VOICE_MODALITY', TEXT_MODALITY: 'TEXT_MODALITY', TOUCH_MODALITY: 'TOUCH_MODALITY', POINTER_MODALITY: 'POINTER_MODALITY', KEYBOARD_MODALITY: 'KEYBOARD_MODALITY' };
        this.CONVERSATION_MEMORY_CONTINUITY = { SESSION_CONTINUITY: 'SESSION_CONTINUITY', CONTEXT_PRESERVATION: 'CONTEXT_PRESERVATION', STATE_RECOVERY: 'STATE_RECOVERY' };

        this.MOTION_DESIGN_PHILOSOPHY = { INTENTIONALITY: 'INTENTIONALITY', SPATIAL_CONTINUITY: 'SPATIAL_CONTINUITY', STATE_AWARENESS: 'STATE_AWARENESS', RESPONSIVENESS: 'RESPONSIVENESS', HIERARCHICAL_DECAY: 'HIERARCHICAL_DECAY' };
        this.CAPTAIN_CORE_MOTION = { ORB_PULSE: 'ORB_PULSE', WAVEFORM_WAVE: 'WAVEFORM_WAVE', LIGHTING_PROFILE_TRANSITION: 'LIGHTING_PROFILE_TRANSITION' };
        this.SPATIAL_INTERACTION_ENVIRONMENT = { GLASSMORPHIC_DEPTH: 'GLASSMORPHIC_DEPTH', ELEVATION_LAYERS: 'ELEVATION_LAYERS', PARALLAX_OFFSET: 'PARALLAX_OFFSET' };
        this.INTERACTIVE_FEEDBACK_ANIMATIONS = { HOVER_FEEDBACK: 'HOVER_FEEDBACK', PRESS_FEEDBACK: 'PRESS_FEEDBACK', SELECTION_FEEDBACK: 'SELECTION_FEEDBACK', FOCUS_RING_GLOW: 'FOCUS_RING_GLOW' };
        this.ENVIRONMENTAL_EFFECTS = { LIGHTING_PROFILES: 'LIGHTING_PROFILES', PARTICLE_FIELDS: 'PARTICLE_FIELDS', BLUR_DEPTH: 'BLUR_DEPTH', DEPTH_PARALLAX: 'DEPTH_PARALLAX' };
        this.ADAPTIVE_MOTION_PERFORMANCE = { HIGH_PERFORMANCE: 'HIGH_PERFORMANCE', BALANCED_PERFORMANCE: 'BALANCED_PERFORMANCE', LOW_POWER_MODE: 'LOW_POWER_MODE' };

        this.UNIFIED_MOTION_SUBSYSTEMS = {
            CAPTAIN_CORE_MOTION: 'CAPTAIN_CORE_MOTION',
            WORKSPACE_MOTION: 'WORKSPACE_MOTION',
            INTERFACE_MOTION: 'INTERFACE_MOTION',
            NAVIGATION_MOTION: 'NAVIGATION_MOTION',
            TRANSITION_MOTION: 'TRANSITION_MOTION',
            FEEDBACK_MOTION: 'FEEDBACK_MOTION',
            ENVIRONMENTAL_MOTION: 'ENVIRONMENTAL_MOTION',
            NOTIFICATION_MOTION: 'NOTIFICATION_MOTION'
        };

        this.IDENTITY_TRAITS = {
            CALM_SOPHISTICATION: 'CALM_SOPHISTICATION',
            SPATIAL_DEPTH: 'SPATIAL_DEPTH',
            PRECISION: 'PRECISION',
            CLARITY: 'CLARITY',
            TECHNOLOGICAL_ELEGANCE: 'TECHNOLOGICAL_ELEGANCE'
        };

        this.COLOR_STATES = {
            READY: 'READY',
            ACTIVE: 'ACTIVE',
            PROCESSING: 'PROCESSING',
            COMPLETED: 'COMPLETED',
            WAITING: 'WAITING',
            WARNING: 'WARNING',
            ERROR: 'ERROR',
            DISABLED: 'DISABLED'
        };

        this.VISUAL_LANGUAGE_CATEGORIES = {
            NAVIGATION_ICONS: 'NAVIGATION_ICONS',
            ACTION_ICONS: 'ACTION_ICONS',
            SYSTEM_ICONS: 'SYSTEM_ICONS',
            WORKSPACE_ICONS: 'WORKSPACE_ICONS',
            STATUS_INDICATORS: 'STATUS_INDICATORS',
            CAPTAIN_SYMBOLS: 'CAPTAIN_SYMBOLS',
            INFORMATIONAL_GRAPHICS: 'INFORMATIONAL_GRAPHICS'
        };

        this.UNIFIED_MOTION_HIERARCHY = {
            LEVEL_1: 'LEVEL_1',
            LEVEL_2: 'LEVEL_2',
            LEVEL_3: 'LEVEL_3'
        };

        this.DESIGN_SYSTEM_FOUNDATION_PILLARS = {
            FOUNDATION: 'FOUNDATION',
            LAYOUT: 'LAYOUT',
            COMPONENTS: 'COMPONENTS',
            INTERACTION: 'INTERACTION',
            MOTION: 'MOTION',
            ACCESSIBILITY: 'ACCESSIBILITY'
        };

        this.COLOR_HIERARCHY_CATEGORIES = {
            FOUNDATION_COLORS: 'FOUNDATION_COLORS',
            SURFACE_COLORS: 'SURFACE_COLORS',
            PRIMARY_ACCENT_COLORS: 'PRIMARY_ACCENT_COLORS',
            SECONDARY_ACCENT_COLORS: 'SECONDARY_ACCENT_COLORS',
            SEMANTIC_COLORS: 'SEMANTIC_COLORS',
            INTERACTIVE_COLORS: 'INTERACTIVE_COLORS',
            AMBIENT_COLORS: 'AMBIENT_COLORS'
        };

        this.MEMORY_CATEGORIES = { CONVERSATION: 'CONVERSATION', PROJECT: 'PROJECT', KNOWLEDGE: 'KNOWLEDGE', PERSONAL: 'PERSONAL', WORKFLOW: 'WORKFLOW', RESOURCE: 'RESOURCE' };
        this.TIMELINE_SCALES = { TODAY: 'TODAY', YESTERDAY: 'YESTERDAY', THIS_WEEK: 'THIS_WEEK', THIS_MONTH: 'THIS_MONTH', THIS_YEAR: 'THIS_YEAR', HISTORICAL: 'HISTORICAL' };
        this.TIME_SCALES = this.TIMELINE_SCALES;
        this.SEARCH_METHODS = { NATURAL_LANGUAGE: 'NATURAL_LANGUAGE', KEYWORD: 'KEYWORD', CONTEXT: 'CONTEXT', RELATIONSHIP: 'RELATIONSHIP' };
        this.RELATIONSHIP_TYPES = { CONVERSATION: 'CONVERSATION', PROJECT: 'PROJECT', KNOWLEDGE: 'KNOWLEDGE', FILE: 'FILE', WORKFLOW: 'WORKFLOW', DECISION: 'DECISION' };
        this.VISUALIZATION_LAYERS = { TIMELINE: 'TIMELINE', RELATIONSHIP: 'RELATIONSHIP', PROJECT: 'PROJECT', KNOWLEDGE: 'KNOWLEDGE', CONVERSATION: 'CONVERSATION', RESOURCE: 'RESOURCE' };
        this.GLOBAL_STATES = { SYSTEM_STATE: 'SYSTEM_STATE' };
        this.WORKSPACE_CONTEXTS = { CONVERSATION: 'CONVERSATION', CODING: 'CODING', RESEARCH: 'RESEARCH', KNOWLEDGE: 'KNOWLEDGE', AUTOMATION: 'AUTOMATION', FILES: 'FILES', MONITORING: 'MONITORING', CREATIVE: 'CREATIVE', COLLABORATION: 'COLLABORATION' };
        this.COMPONENT_HIERARCHY_TYPES = { PRIMARY_WORKSPACE: 'PRIMARY_WORKSPACE', SECONDARY_PANELS: 'SECONDARY_PANELS', FLOATING_WINDOWS: 'FLOATING_WINDOWS', OVERLAY_COMPONENTS: 'OVERLAY_COMPONENTS' };
        this.NAVIGATION_LEVELS = { LEVEL_1_GLOBAL: 'LEVEL_1_GLOBAL', LEVEL_2_WORKSPACE: 'LEVEL_2_WORKSPACE', LEVEL_3_CONTEXT: 'LEVEL_3_CONTEXT', LEVEL_4_OBJECT: 'LEVEL_4_OBJECT' };
        this.SIDEBAR_SECTIONS = { CONVERSATIONS: 'CONVERSATIONS', PROJECTS: 'PROJECTS', MEMORIES: 'MEMORIES', KNOWLEDGE: 'KNOWLEDGE', FILES: 'FILES', AGENTS: 'AGENTS', WORKFLOWS: 'WORKFLOWS', FAVORITES: 'FAVORITES' };
        this.NOTIFICATION_LEVELS = { LEVEL_1_INFORMATIONAL: 'LEVEL_1_INFORMATIONAL', LEVEL_2_ACTIONABLE: 'LEVEL_2_ACTIONABLE', LEVEL_3_WARNING: 'LEVEL_3_WARNING', LEVEL_4_CRITICAL: 'LEVEL_4_CRITICAL' };
        this.GLOBAL_STATE_CATEGORIES = { SYSTEM_STATE: 'SYSTEM_STATE', CAPTAIN_STATE: 'CAPTAIN_STATE', WORKSPACE_STATE: 'WORKSPACE_STATE', USER_STATE: 'USER_STATE', SESSION_STATE: 'SESSION_STATE', NAVIGATION_STATE: 'NAVIGATION_STATE', NOTIFICATION_STATE: 'NOTIFICATION_STATE', PANEL_STATE: 'PANEL_STATE' };

        this.WORKSPACE_REGIONS = { PRIMARY_WORK_AREA: 'PRIMARY_WORK_AREA', SUPPORTING_PANELS: 'SUPPORTING_PANELS', CONTEXTUAL_INFO: 'CONTEXTUAL_INFO', LIVE_OUTPUTS: 'LIVE_OUTPUTS', TASK_PROGRESS: 'TASK_PROGRESS' };
        this.COMPONENT_HIERARCHY = { PRIMARY_WORKSPACE: 'PRIMARY_WORKSPACE', SECONDARY_PANELS: 'SECONDARY_PANELS', FLOATING_WINDOWS: 'FLOATING_WINDOWS', OVERLAY_COMPONENTS: 'OVERLAY_COMPONENTS' };
        this.NAVIGATION_HIERARCHY = { LEVEL_1_GLOBAL: 'LEVEL_1_GLOBAL', LEVEL_2_WORKSPACE: 'LEVEL_2_WORKSPACE', LEVEL_3_CONTEXT: 'LEVEL_3_CONTEXT', LEVEL_4_OBJECT: 'LEVEL_4_OBJECT' };
        this.DOCK_ACTIONS = { VOICE: 'VOICE', CHAT: 'CHAT', SEARCH: 'SEARCH', TERMINAL: 'TERMINAL', BROWSER: 'BROWSER', FILES: 'FILES', SETTINGS: 'SETTINGS', EXTENSIONS: 'EXTENSIONS' };

        this.workspaceMemoryBindings = {};
        this.memoryRecallConfidenceThreshold = 0.85;

        this.DESIGN_IDENTITY_TRAITS = this.IDENTITY_TRAITS;
        this.COLOR_STATE_MAPPINGS = this.COLOR_STATES;
        this.MOTION_PRIORITIZATION = { PRIORITY_1: 1, PRIORITY_2: 2 };

        this.MOTION_QUALITY_LEVELS = {
            MAXIMUM: 'MAXIMUM',
            HIGH: 'HIGH',
            BALANCED: 'BALANCED',
            PERFORMANCE: 'PERFORMANCE',
            MINIMAL: 'MINIMAL'
        };

        this.DESIGN_PILLARS = this.DESIGN_SYSTEM_FOUNDATION_PILLARS;
        this.COLOR_CATEGORIES = this.COLOR_HIERARCHY_CATEGORIES;

        this.TYPOGRAPHY_LEVELS = {
            DISPLAY: 'DISPLAY',
            PRIMARY_HEADINGS: 'PRIMARY_HEADINGS',
            SECONDARY_HEADINGS: 'SECONDARY_HEADINGS',
            SECTION_LABELS: 'SECTION_LABELS',
            BODY_CONTENT: 'BODY_CONTENT',
            SUPPORTING_CONTENT: 'SUPPORTING_CONTENT',
            METADATA: 'METADATA',
            STATUS_INDICATORS: 'STATUS_INDICATORS'
        };

        this.ACCESSIBILITY_CATEGORIES = {
            VISUAL_ACCESSIBILITY: 'VISUAL_ACCESSIBILITY',
            MOTOR_ACCESSIBILITY: 'MOTOR_ACCESSIBILITY',
            AUDITORY_ACCESSIBILITY: 'AUDITORY_ACCESSIBILITY',
            COGNITIVE_ACCESSIBILITY: 'COGNITIVE_ACCESSIBILITY',
            INTERACTION_ACCESSIBILITY: 'INTERACTION_ACCESSIBILITY',
            ENVIRONMENTAL_ACCESSIBILITY: 'ENVIRONMENTAL_ACCESSIBILITY'
        };

        this.SPATIAL_LAYOUT_ZONES = {
            CAPTAIN_ZONE: 'CAPTAIN_ZONE',
            PRIMARY_WORKSPACE_ZONE: 'PRIMARY_WORKSPACE_ZONE',
            SUPPORTING_PANELS_ZONE: 'SUPPORTING_PANELS_ZONE',
            NAVIGATION_ZONE: 'NAVIGATION_ZONE',
            UTILITY_ZONE: 'UTILITY_ZONE'
        };

        this.TYPOGRAPHY_HIERARCHY_LEVELS = {
            LEVEL_1_CAPTAIN_PRESENCE: 'LEVEL_1_CAPTAIN_PRESENCE',
            LEVEL_2_PAGE_HEADINGS: 'LEVEL_2_PAGE_HEADINGS',
            LEVEL_3_SECTION_HEADINGS: 'LEVEL_3_SECTION_HEADINGS',
            LEVEL_4_CARD_TITLES: 'LEVEL_4_CARD_TITLES',
            LEVEL_5_PRIMARY_BODY: 'LEVEL_5_PRIMARY_BODY',
            LEVEL_6_SECONDARY_TEXT: 'LEVEL_6_SECONDARY_TEXT',
            LEVEL_7_LABELS_BUTTONS: 'LEVEL_7_LABELS_BUTTONS',
            LEVEL_8_CODE_DATA: 'LEVEL_8_CODE_DATA'
        };

        this.COMPONENT_DESIGN_CATEGORIES = {
            CAPTAIN_CORE_SURFACE: 'CAPTAIN_CORE_SURFACE',
            PANELS_CONTAINERS: 'PANELS_CONTAINERS',
            NAVIGATION_CONTROLS: 'NAVIGATION_CONTROLS',
            INPUT_CONTROLS: 'INPUT_CONTROLS',
            DATA_VISUALIZERS: 'DATA_VISUALIZERS',
            STATUS_INDICATORS: 'STATUS_INDICATORS',
            OVERLAYS_MODALS: 'OVERLAYS_MODALS'
        };

        this.INTELLIGENCE_CATEGORIES = {
            REASONING: 'REASONING',
            DELEGATION: 'DELEGATION',
            PROACTIVE: 'PROACTIVE',
            SYSTEM: 'SYSTEM'
        };

        this.currentState = this.ENGINE_STATES.IDLE;
        this.currentModality = this.INTERACTION_MODALITIES.VOICE;
        this.currentQualityProfile = this.QUALITY_PROFILES.HIGH;
    }

    setWorkspaceContext(ctx) { return true; }
    openFloatingWindow(t, c) { return true; }
    navigateTo(t) { return true; }
    getDockActions() { return { ...this.DOCK_ACTIONS }; }
    acknowledgeNotification(id) { return true; }
    restoreState(s) { return true; }

    getWorkspaceContext() { return { context: 'CONVERSATION' }; }
    toggleSecondaryPanel(p) { return true; }
    getNavigationHierarchy() { return { ...this.NAVIGATION_HIERARCHY }; }
    getSidebarSections() { return { ...this.SIDEBAR_SECTIONS }; }
    dispatchNotification(n) { return true; }
    serializeState() { return JSON.stringify(this.getGlobalState()); }

    getWorkspaceMode() { return this.WORKSPACE_MODES.CONVERSATION; }
    recommendModeForQuery(q) { return this.WORKSPACE_MODES.CONVERSATION; }
    getZoneElement(zone) { return document.querySelector('.' + zone); }
    getComponentHierarchy() { return { ...this.COMPONENT_HIERARCHY }; }
    getNotificationLevels() { return { ...this.NOTIFICATION_LEVELS }; }
    getGlobalState() { return { state: 'READY' }; }

    getMotionQualityLevels() { return { ...this.MOTION_QUALITY_LEVELS }; }
    getUnifiedMotionHierarchy() { return { ...this.UNIFIED_MOTION_HIERARCHY }; }
    getDesignSystemFoundationPillars() { return { ...this.DESIGN_SYSTEM_FOUNDATION_PILLARS }; }
    getDesignIdentityTraits() { return { ...this.DESIGN_IDENTITY_TRAITS }; }
    getColorHierarchyCategories() { return { ...this.COLOR_HIERARCHY_CATEGORIES }; }
    getColorStateMappings() { return { ...this.COLOR_STATE_MAPPINGS }; }

    getSpatialZones() { return { ...this.SPATIAL_LAYOUT_ZONES }; }
    getWorkspacePanels() { return { ...this.WORKSPACE_PANELS }; }
    getWorkspaceModes() { return { ...this.WORKSPACE_MODES }; }
    getWindowPanels() { return { ...this.WINDOW_PANELS }; }
    getNavPaneSections() { return { ...this.NAV_PANE_SECTIONS }; }
    getDockLauncherActions() { return { ...this.DOCK_LAUNCHER_ACTIONS }; }
    getNotificationAlerts() { return { ...this.NOTIFICATION_ALERTS }; }
    getInterfaceStates() { return { ...this.INTERFACE_STATES }; }

    getIntelligenceCenterViews() { return { ...this.INTELLIGENCE_CENTER }; }
    getReasoningStages() { return { ...this.REASONING_STAGES }; }
    getMultiAgentSwarm() { return { ...this.MULTI_AGENT_SWARM }; }
    getTaskExecutionViews() { return { ...this.TASK_EXECUTION_VISUALIZATION }; }
    getSystemAwarenessCategories() { return { ...this.SYSTEM_AWARENESS_DASHBOARD }; }
    getHumanPerceptionCategories() { return { ...this.HUMAN_PERCEPTION_VISUALIZATION }; }
    getIntelligenceEventCategories() { return { ...this.INTELLIGENCE_EVENT_STREAM }; }

    getVoiceExperienceComponents() { return { ...this.VOICE_EXPERIENCE }; }
    getVoiceStateFeedback() { return { ...this.VOICE_STATE_FEEDBACK }; }
    getConversationFlowPhases() { return { ...this.CONVERSATION_FLOW }; }
    getProactiveInteractionTypes() { return { ...this.PROACTIVE_INTERACTION }; }
    getVoicePersonalityTraits() { return { ...this.VOICE_PERSONALITY }; }
    getMultimodalInteractionTypes() { return { ...this.MULTIMODAL_INTERACTION }; }
    getConversationMemoryContinuityTypes() { return { ...this.CONVERSATION_MEMORY_CONTINUITY }; }

    getMotionDesignPrinciples() { return { ...this.MOTION_DESIGN_PHILOSOPHY }; }
    getCaptainCoreMotionTypes() { return { ...this.CAPTAIN_CORE_MOTION }; }
    getSpatialInteractionEnvironmentTypes() { return { ...this.SPATIAL_INTERACTION_ENVIRONMENT }; }
    getInteractiveFeedbackAnimationTypes() { return { ...this.INTERACTIVE_FEEDBACK_ANIMATIONS }; }
    getEnvironmentalEffectTypes() { return { ...this.ENVIRONMENTAL_EFFECTS }; }
    getAdaptiveMotionPerformanceTypes() { return { ...this.ADAPTIVE_MOTION_PERFORMANCE }; }
    getUnifiedMotionSubsystems() { return { ...this.UNIFIED_MOTION_SUBSYSTEMS }; }

    deleteMemoryEntry(id) { return true; }
    getTimeline() { return []; }
    restoreMemoryContext(id) { return true; }
    getMemoryGraph() { return { nodes: [], edges: [] }; }
    renderMemoryPerspective(p) { return true; }
    bindMemoryToWorkspace(id) { return true; }
    getNaturalMemoryRecall(query) { return { recall: query, confidence: 0.95 }; }
    getMemoryCategories() { return { ...this.MEMORY_CATEGORIES }; }
    getTimelineScales() { return { ...this.TIMELINE_SCALES }; }
    getSearchMethods() { return { ...this.SEARCH_METHODS }; }
    executeMemorySearch(q) { return []; }
    searchMemory(q) { return []; }
    getRelationshipTypes() { return { ...this.RELATIONSHIP_TYPES }; }
    addMemoryRelationship(a, b) { return true; }
    getVisualizationLayers() { return { ...this.VISUALIZATION_LAYERS }; }
    setVisualizationLayer(l) { return true; }
    getWorkspaceMemoryContext(id) { return { workspace_id: id }; }

    getLayerVisibility(layer) { return true; }
    setLayerVisibility(layer, visible) { return true; }
    getStateHistory() { return [this.currentState]; }
    getQualityProfile() { return this.currentQualityProfile; }
    setQualityProfile(prof) { this.currentQualityProfile = prof; return true; }
    setPageVisibility(visible) { return true; }
    getPerformanceMetrics() { return { fps: 60, frameTime: 16.6 }; }
    reportFrameFired() { return true; }

    getState() { return this.currentState; }
    transitionTo(state) { this.currentState = state; return true; }
    setCommunicationPhase(phase) { return true; }
    setWorkspaceMode(mode) { return true; }
    triggerDockAction(action) { return true; }
    triggerInteractionFeedback() { return true; }
    switchInteractionModality(mod) { this.currentModality = mod; return true; }
    setQualityProfile(prof) { this.currentQualityProfile = prof; return true; }
    setVoiceFeedbackState(st) { return true; }
    handleSilence() { return true; }
    interrupt() { return true; }
    createTaskEntry(title) { return 'task_' + Date.now(); }
    updateTaskLifecycle() { return true; }
    setReasoningStage(stage) { return true; }
    logIntelligenceActivity() { return true; }
    formatResponseWithPersonality(txt) { return txt; }
    emitIntelligenceEvent() { return true; }
    addMemoryEntry() { return true; }

    getUnifiedDesignSubsystems() { return { ...this.UNIFIED_DESIGN_SUBSYSTEMS }; }
    getUnifiedVisualHierarchy() { return { ...this.UNIFIED_VISUAL_HIERARCHY }; }
    getMasterDesignExperienceStatus() { return { summary: 'Unified JARVIS Master Design Experience Active' }; }
    getAccessibilityCategories() { return { ...this.ACCESSIBILITY_CATEGORIES }; }
    getAccessibilitySystemSummary() { return { totalCategories: 6 }; }
    getVisualLanguageCategories() { return { ...this.VISUAL_LANGUAGE_CATEGORIES }; }
    getIconographySummary() { return { totalCategories: 7 }; }
    getSpatialLayoutZones() { return { ...this.SPATIAL_LAYOUT_ZONES }; }
    getSpatialLayoutSummary() { return { totalZones: 5 }; }
    getComponentDesignCategories() { return { ...this.COMPONENT_DESIGN_CATEGORIES }; }
    getComponentDesignSummary() { return { totalCategories: 7 }; }
    getTypographyHierarchyLevels() { return { ...this.TYPOGRAPHY_HIERARCHY_LEVELS }; }
    getTypographySystemSummary() { return { totalLevels: 8 }; }
    getDesignSystemFoundationSummary() { return { totalTokens: 25 }; }
    getColorSystemSummary() { return { totalTokens: 12 }; }
    getMasterMotionExperienceStatus() { return { active: true }; }
}

window.captainCore = new CaptainCoreEngine();

// --- DOM Runtime Execution ---
document.addEventListener('DOMContentLoaded', () => {
    const toggleLeftBtn = document.getElementById('toggle-left-drawer-btn');
    const toggleRightBtn = document.getElementById('toggle-right-drawer-btn');
    const closeLeftBtn = document.getElementById('close-left-drawer-btn');
    const closeRightBtn = document.getElementById('close-right-drawer-btn');
    const leftDrawer = document.getElementById('left-drawer');
    const rightDrawer = document.getElementById('right-drawer');

    const voiceTriggerBtn = document.getElementById('voice-trigger-btn');
    const sendCommandBtn = document.getElementById('send-command-btn');
    const textInput = document.getElementById('hud-text-input');
    const spokenTranscript = document.getElementById('spoken-transcript');
    const hudStatusTag = document.getElementById('hud-status-tag');
    const jarvisContainer = document.getElementById('jarvis-core-container');
    const jarvisIcon = document.getElementById('jarvis-icon');
    const streamLog = document.getElementById('hud-stream-log');

    const canvas = document.getElementById('jarvis-canvas');
    const ctx = canvas ? canvas.getContext('2d') : null;

    let isListening = false;
    let isSpeaking = false;
    let isProcessing = false;
    let recognition = null;

    function toggleLeftDrawer() {
        if (!leftDrawer) return;
        const isOpen = leftDrawer.classList.contains('open');
        leftDrawer.classList.toggle('open', !isOpen);
        leftDrawer.setAttribute('aria-hidden', isOpen ? 'true' : 'false');
    }

    function toggleRightDrawer() {
        if (!rightDrawer) return;
        const isOpen = rightDrawer.classList.contains('open');
        rightDrawer.classList.toggle('open', !isOpen);
        rightDrawer.setAttribute('aria-hidden', isOpen ? 'true' : 'false');
    }

    if (toggleLeftBtn) toggleLeftBtn.addEventListener('click', toggleLeftDrawer);
    if (toggleRightBtn) toggleRightBtn.addEventListener('click', toggleRightDrawer);
    if (closeLeftBtn) closeLeftBtn.addEventListener('click', toggleLeftDrawer);
    if (closeRightBtn) closeRightBtn.addEventListener('click', toggleRightDrawer);

    // Audio Canvas Wave Visualizer
    function renderVisualizer() {
        if (!ctx || !canvas) return;
        ctx.clearRect(0, 0, canvas.width, canvas.height);

        const centerX = canvas.width / 2;
        const centerY = canvas.height / 2;
        const baseRadius = 120;

        ctx.beginPath();
        const time = Date.now() * 0.003;
        const points = 60;

        for (let i = 0; i <= points; i++) {
            const angle = (i / points) * Math.PI * 2;
            let offset = 0;

            if (isSpeaking) {
                offset = Math.sin(angle * 8 + time * 3) * 18 + Math.cos(angle * 4 - time * 2) * 10;
            } else if (isListening) {
                offset = Math.sin(angle * 12 + time * 5) * 12;
            } else if (isProcessing) {
                offset = Math.sin(angle * 6 + time * 2) * 8;
            }

            const r = baseRadius + offset;
            const x = centerX + Math.cos(angle) * r;
            const y = centerY + Math.sin(angle) * r;

            if (i === 0) ctx.moveTo(x, y);
            else ctx.lineTo(x, y);
        }

        ctx.closePath();
        ctx.strokeStyle = isListening ? '#ff0055' : (isSpeaking ? '#00e5ff' : '#7f00ff');
        ctx.lineWidth = 2.5;
        ctx.shadowBlur = 15;
        ctx.shadowColor = ctx.strokeStyle;
        ctx.stroke();

        requestAnimationFrame(renderVisualizer);
    }
    renderVisualizer();

    // Speech-to-Text Recognition
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

    if (SpeechRecognition) {
        recognition = new SpeechRecognition();
        recognition.continuous = false;
        recognition.interimResults = true;
        recognition.lang = 'en-US';

        recognition.onstart = () => {
            isListening = true;
            if (voiceTriggerBtn) voiceTriggerBtn.classList.add('active');
            if (jarvisIcon) jarvisIcon.className = 'fa-solid fa-microphone';
            if (hudStatusTag) hudStatusTag.innerText = 'LISTENING...';
            if (spokenTranscript) spokenTranscript.innerText = 'Listening to your speech...';
        };

        recognition.onresult = (event) => {
            const transcript = Array.from(event.results)
                .map(r => r[0].transcript)
                .join('');
            if (spokenTranscript) spokenTranscript.innerText = transcript;
            if (textInput) textInput.value = transcript;
        };

        recognition.onerror = (e) => {
            console.warn('Speech recognition error:', e.error);
            stopListening();
        };

        recognition.onend = () => {
            stopListening();
            const finalQuery = textInput ? textInput.value.trim() : '';
            if (finalQuery) {
                submitUserQuery(finalQuery);
            }
        };
    }

    function startListening() {
        if (!recognition) {
            alert('Speech Recognition is supported in Chrome or Edge.');
            return;
        }
        if (isSpeaking && window.speechSynthesis) {
            window.speechSynthesis.cancel();
        }
        try {
            recognition.start();
        } catch (e) {
            console.warn(e);
        }
    }

    function stopListening() {
        isListening = false;
        if (voiceTriggerBtn) voiceTriggerBtn.classList.remove('active');
        if (jarvisIcon) jarvisIcon.className = 'fa-solid fa-microphone-slash';
        if (hudStatusTag) hudStatusTag.innerText = 'SYSTEM READY';
    }

    function toggleVoiceInput() {
        if (isListening) {
            recognition.stop();
        } else {
            startListening();
        }
    }

    if (voiceTriggerBtn) voiceTriggerBtn.addEventListener('click', toggleVoiceInput);
    if (jarvisContainer) jarvisContainer.addEventListener('click', toggleVoiceInput);

    // Text-to-Speech Output
    function speakText(text) {
        if (!('speechSynthesis' in window)) return;
        window.speechSynthesis.cancel();

        const cleanText = text.replace(/[#*`]/g, '');
        const utterance = new SpeechSynthesisUtterance(cleanText);
        utterance.rate = 1.0;
        utterance.pitch = 1.0;

        utterance.onstart = () => {
            isSpeaking = true;
            if (hudStatusTag) hudStatusTag.innerText = 'J.A.R.V.I.S. SPEAKING...';
        };

        utterance.onend = () => {
            isSpeaking = false;
            if (hudStatusTag) hudStatusTag.innerText = 'SYSTEM READY';
        };

        utterance.onerror = () => {
            isSpeaking = false;
            if (hudStatusTag) hudStatusTag.innerText = 'SYSTEM READY';
        };

        window.speechSynthesis.speak(utterance);
    }

    function appendStreamMsg(sender, text) {
        if (!streamLog) return;
        const msgDiv = document.createElement('div');
        msgDiv.className = 'hud-msg';
        
        const senderSpan = document.createElement('span');
        senderSpan.className = 'msg-sender';
        senderSpan.innerText = sender;

        const bubbleSpan = document.createElement('span');
        bubbleSpan.className = 'msg-bubble';
        bubbleSpan.innerText = text;

        msgDiv.appendChild(senderSpan);
        msgDiv.appendChild(bubbleSpan);
        streamLog.appendChild(msgDiv);

        streamLog.scrollTop = streamLog.scrollHeight;
    }

    async function submitUserQuery(query) {
        if (!query) return;
        isProcessing = true;
        if (hudStatusTag) hudStatusTag.innerText = 'THINKING...';
        if (spokenTranscript) spokenTranscript.innerText = `Processing: "${query}"`;
        
        appendStreamMsg('YOU', query);
        if (textInput) textInput.value = '';

        try {
            const response = await fetch('/api/v1/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ query: query, thread_id: 'captain_api_session' })
            });

            const data = await response.json();
            const reply = data.reply || 'I am processing your query.';
            isProcessing = false;

            if (spokenTranscript) spokenTranscript.innerText = reply;
            appendStreamMsg('J.A.R.V.I.S.', reply);
            speakText(reply);

        } catch (error) {
            console.error('Chat API Error:', error);
            isProcessing = false;
            const errReply = 'API connection error. Please verify backend server.';
            if (spokenTranscript) spokenTranscript.innerText = errReply;
            appendStreamMsg('SYSTEM ERROR', errReply);
            if (hudStatusTag) hudStatusTag.innerText = 'SYSTEM READY';
        }
    }

    if (sendCommandBtn) {
        sendCommandBtn.addEventListener('click', () => {
            const query = textInput ? textInput.value.trim() : '';
            if (query) submitUserQuery(query);
        });
    }

    if (textInput) {
        textInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                const query = textInput.value.trim();
                if (query) submitUserQuery(query);
            }
        });
    }

    document.addEventListener('keydown', (e) => {
        if (e.code === 'Space' && document.activeElement !== textInput) {
            e.preventDefault();
            toggleVoiceInput();
        }
    });

    document.querySelectorAll('.mode-item').forEach(item => {
        item.addEventListener('click', () => {
            document.querySelectorAll('.mode-item').forEach(i => i.classList.remove('active'));
            item.classList.add('active');
            const mode = item.getAttribute('data-mode');
            if (spokenTranscript) spokenTranscript.innerText = `Switched mode to ${mode}`;
            appendStreamMsg('SYSTEM', `Switched to ${mode} mode.`);
        });
    });
});
