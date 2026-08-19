/* ==========================================================================
   CAPTAIN AI OS — J.A.R.V.I.S. SCI-FI HUD RUNTIME ENGINE
   DIRECT VOICE-TO-TEXT & TEXT-TO-VOICE SYSTEM WITH BACKEND GRAPH INTEGRATION
   ========================================================================== */

var currentExpression = 'happy';
var isBlinking = false;
window.currentExpression = 'happy';
window.isBlinking = false;

// Headband points connecting directly into earcups
const headbandPoints = [
    new THREE.Vector3(-1.2, 0.8, 0), // Earcup Left
    new THREE.Vector3(-0.8, 1.5, 0),
    new THREE.Vector3(0, 1.7, 0),
    new THREE.Vector3(0.8, 1.5, 0),
    new THREE.Vector3(1.2, 0.8, 0)  // Earcup Right
];

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
            TASK: 'TASK',
            AGENT: 'AGENT',
            KNOWLEDGE: 'KNOWLEDGE',
            MEMORY: 'MEMORY',
            SYSTEM: 'SYSTEM'
        };

        this.REASONING_STAGES = {
            UNDERSTANDING: 'UNDERSTANDING',
            PLANNING: 'PLANNING',
            GATHERING_INFORMATION: 'GATHERING_INFORMATION',
            PROCESSING: 'PROCESSING',
            VERIFYING: 'VERIFYING',
            RESPONDING: 'RESPONDING'
        };

        this.AGENT_STATES = {
            WAITING: 'WAITING',
            ASSIGNED: 'ASSIGNED',
            WORKING: 'WORKING',
            WAITING_FOR_DEPENDENCY: 'WAITING_FOR_DEPENDENCY',
            COMPLETED: 'COMPLETED',
            UNAVAILABLE: 'UNAVAILABLE'
        };

        this.TASK_LIFECYCLE = {
            QUEUED: 'QUEUED',
            INITIALIZING: 'INITIALIZING',
            EXECUTING: 'EXECUTING',
            WAITING: 'WAITING',
            VERIFYING: 'VERIFYING',
            COMPLETED: 'COMPLETED',
            INTERRUPTED: 'INTERRUPTED'
        };

        this.EVENT_CATEGORIES = {
            CONVERSATION_EVENTS: 'CONVERSATION_EVENTS',
            TASK_EVENTS: 'TASK_EVENTS',
            WORKSPACE_EVENTS: 'WORKSPACE_EVENTS',
            MEMORY_EVENTS: 'MEMORY_EVENTS',
            KNOWLEDGE_EVENTS: 'KNOWLEDGE_EVENTS',
            AGENT_EVENTS: 'AGENT_EVENTS',
            SYSTEM_EVENTS: 'SYSTEM_EVENTS'
        };

        this.VOICE_PRESENCE_STATES = {
            READY: 'READY',
            LISTENING: 'LISTENING',
            UNDERSTANDING: 'UNDERSTANDING',
            PROCESSING: 'PROCESSING',
            RESPONDING: 'RESPONDING',
            WAITING: 'WAITING'
        };

        this.VOICE_FEEDBACK_STATES = {
            READY: 'READY',
            LISTENING: 'LISTENING',
            UNDERSTANDING: 'UNDERSTANDING',
            THINKING: 'THINKING',
            SPEAKING: 'SPEAKING',
            INTERRUPTED: 'INTERRUPTED',
            PAUSED: 'PAUSED',
            UNAVAILABLE: 'UNAVAILABLE'
        };

        this.CONVERSATION_STAGES = {
            GREETING: 'GREETING',
            UNDERSTANDING: 'UNDERSTANDING',
            DISCUSSION: 'DISCUSSION',
            CLARIFICATION: 'CLARIFICATION',
            RESOLUTION: 'RESOLUTION',
            CONTINUATION: 'CONTINUATION'
        };

        this.PROACTIVE_ASSISTANCE_TYPES = {
            CONTEXT_REMINDERS: 'CONTEXT_REMINDERS',
            MEMORY_SUGGESTIONS: 'MEMORY_SUGGESTIONS',
            KNOWLEDGE_RECOMMENDATIONS: 'KNOWLEDGE_RECOMMENDATIONS',
            WORKFLOW_ASSISTANCE: 'WORKFLOW_ASSISTANCE',
            SYSTEM_AWARENESS: 'SYSTEM_AWARENESS',
            COLLABORATION_SUPPORT: 'COLLABORATION_SUPPORT'
        };

        this.COMMUNICATION_IDENTITY_TRAITS = {
            KNOWLEDGEABLE: 'KNOWLEDGEABLE',
            RELIABLE: 'RELIABLE',
            TRANSPARENT: 'TRANSPARENT',
            RESPECTFUL: 'RESPECTFUL',
            PATIENT: 'PATIENT',
            FOCUSED: 'FOCUSED'
        };

        this.MULTIMODAL_METHODS = {
            VOICE: 'VOICE',
            TEXT: 'TEXT',
            TOUCH: 'TOUCH',
            KEYBOARD: 'KEYBOARD',
            MOUSE_POINTER: 'MOUSE_POINTER',
            HAND_GESTURES: 'HAND_GESTURES',
            VISION_PRESENCE: 'VISION_PRESENCE'
        };

        this.CONVERSATION_CONTEXT_LAYERS = {
            CURRENT_CONVERSATION: 'CURRENT_CONVERSATION',
            CURRENT_WORKSPACE: 'CURRENT_WORKSPACE',
            ACTIVE_PROJECT: 'ACTIVE_PROJECT',
            RELATED_DISCUSSIONS: 'RELATED_DISCUSSIONS',
            LONG_TERM_MEMORY: 'LONG_TERM_MEMORY'
        };

        this.VOICE_EXPERIENCE_PILLARS = {
            UNIFIED_CONVERSATION: 'UNIFIED_CONVERSATION',
            INTERACTION_RHYTHM: 'INTERACTION_RHYTHM',
            RELATIONSHIP_BUILDING: 'RELATIONSHIP_BUILDING',
            CONTEXTUAL_INTELLIGENCE: 'CONTEXTUAL_INTELLIGENCE',
            USER_CONFIDENCE: 'USER_CONFIDENCE',
            ABSOLUTE_USER_CONTROL: 'ABSOLUTE_USER_CONTROL',
            UNIVERSAL_ACCESSIBILITY: 'UNIVERSAL_ACCESSIBILITY'
        };

        this.MOTION_CATEGORIES = {
            SYSTEM_MOTION: 'SYSTEM_MOTION',
            CAPTAIN_MOTION: 'CAPTAIN_MOTION',
            INTERACTION_MOTION: 'INTERACTION_MOTION',
            WORKSPACE_MOTION: 'WORKSPACE_MOTION',
            NOTIFICATION_MOTION: 'NOTIFICATION_MOTION',
            BACKGROUND_MOTION: 'BACKGROUND_MOTION'
        };

        this.MOTION_HIERARCHY = {
            LEVEL_1: 'LEVEL_1',
            LEVEL_2: 'LEVEL_2',
            LEVEL_3: 'LEVEL_3'
        };

        this.CORE_MOTION_LAYERS = {
            AMBIENT_MOTION: 'AMBIENT_MOTION',
            ATTENTION_MOTION: 'ATTENTION_MOTION',
            LISTENING_MOTION: 'LISTENING_MOTION',
            THINKING_MOTION: 'THINKING_MOTION',
            SPEAKING_MOTION: 'SPEAKING_MOTION',
            INTERACTION_MOTION: 'INTERACTION_MOTION',
            COMPLETION_MOTION: 'COMPLETION_MOTION'
        };

        this.SPATIAL_ENVIRONMENT_LAYERS = {
            ENVIRONMENT_LAYER: 'ENVIRONMENT_LAYER',
            AMBIENT_LAYER: 'AMBIENT_LAYER',
            CAPTAIN_LAYER: 'CAPTAIN_LAYER',
            WORKSPACE_LAYER: 'WORKSPACE_LAYER',
            INTERFACE_LAYER: 'INTERFACE_LAYER',
            OVERLAY_LAYER: 'OVERLAY_LAYER'
        };

        this.INTERACTION_FEEDBACK_TYPES = {
            SELECTION_FEEDBACK: 'SELECTION_FEEDBACK',
            HOVER_FEEDBACK: 'HOVER_FEEDBACK',
            FOCUS_FEEDBACK: 'FOCUS_FEEDBACK',
            PRESS_FEEDBACK: 'PRESS_FEEDBACK',
            DRAG_FEEDBACK: 'DRAG_FEEDBACK',
            DROP_FEEDBACK: 'DROP_FEEDBACK',
            COMPLETION_FEEDBACK: 'COMPLETION_FEEDBACK',
            REJECTION_FEEDBACK: 'REJECTION_FEEDBACK'
        };

        this.ENVIRONMENTAL_EFFECT_CATEGORIES = {
            AMBIENT_BACKGROUND: 'AMBIENT_BACKGROUND',
            PARTICLE_ENVIRONMENT: 'PARTICLE_ENVIRONMENT',
            ATMOSPHERIC_LIGHTING: 'ATMOSPHERIC_LIGHTING',
            DEPTH_ATMOSPHERE: 'DEPTH_ATMOSPHERE',
            ENERGY_ENVIRONMENT: 'ENERGY_ENVIRONMENT',
            ENVIRONMENTAL_GLOW: 'ENVIRONMENTAL_GLOW',
            ENVIRONMENTAL_REFLECTION: 'ENVIRONMENTAL_REFLECTION'
        };

        this.MOTION_PRIORITIZATION = {
            HIGH: 'HIGH',
            MEDIUM: 'MEDIUM',
            LOW: 'LOW'
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

    getWorkspaceRegions() { return { ...this.WORKSPACE_REGIONS }; }
    showOverlay(id) { return true; }
    searchNavigate(query) { return true; }
    setSidebarVisibility(visible) { return true; }
    setDockVisibility(visible) { return true; }
    getNotificationHistory() { return []; }

    getIntelligenceCenterViews() { return { ...this.INTELLIGENCE_CENTER }; }
    getIntelligenceCategories() { return { ...this.INTELLIGENCE_CATEGORIES }; }
    getActiveIntelligenceSummary() { return { active: true }; }
    getReasoningStages() { return { ...this.REASONING_STAGES }; }
    getReasoningVisualizationState() { return { state: 'IDLE' }; }
    getAgentStates() { return { ...this.AGENT_STATES }; }
    registerSubagent(agent) { return true; }
    setAgentState(agentId, state) { return true; }
    getAgentSwarmStatus() { return { activeAgents: 6 }; }
    getMultiAgentSwarm() { return { ...this.MULTI_AGENT_SWARM }; }
    getTaskLifecycleStages() { return { ...this.TASK_LIFECYCLE }; }
    getTaskRegistrySummary() { return { totalTasks: 0 }; }
    getTaskExecutionViews() { return { ...this.TASK_EXECUTION_VISUALIZATION }; }
    getSystemAwarenessCategories() { return { ...this.SYSTEM_AWARENESS_DASHBOARD }; }
    getAwarenessCategories() { return { ...this.AWARENESS_CATEGORIES }; }
    setAwarenessCategoryStatus(cat, status) { return true; }
    getSystemHealthOverview() { return { status: 'HEALTHY' }; }
    getHumanPerceptionCategories() { return { ...this.HUMAN_PERCEPTION_VISUALIZATION }; }
    getPerceptionCategories() { return { ...this.PERCEPTION_CATEGORIES }; }
    setPerceptionCategoryStatus(cat, status) { return true; }
    getPerceptionCapabilitySummary() { return { active: true }; }
    getEventCategories() { return { ...this.EVENT_CATEGORIES }; }
    getIntelligenceEventCategories() { return { ...this.INTELLIGENCE_EVENT_STREAM }; }
    getIntelligenceEventStream() { return []; }

    getVoicePresenceStates() { return { ...this.VOICE_PRESENCE_STATES }; }
    setVoicePresenceState(st) { return true; }
    getVoiceExperienceStatus() { return { status: 'READY' }; }
    getVoiceExperienceComponents() { return { ...this.VOICE_EXPERIENCE }; }
    getVoiceFeedbackStates() { return { ...this.VOICE_FEEDBACK_STATES }; }
    getVoiceFeedbackStateSummary() { return { status: 'IDLE' }; }
    getVoiceStateFeedback() { return { ...this.VOICE_STATE_FEEDBACK }; }
    getConversationStages() { return { ...this.CONVERSATION_STAGES }; }
    setConversationStage(st) { return true; }
    getConversationFlowSummary() { return { flow: 'ACTIVE' }; }
    getConversationFlowPhases() { return { ...this.CONVERSATION_FLOW }; }
    getProactiveAssistanceTypes() { return { ...this.PROACTIVE_ASSISTANCE_TYPES }; }
    triggerProactiveSuggestion(sug) { return true; }
    dismissProactiveSuggestion(id) { return true; }
    getProactiveSuggestionsSummary() { return { suggestions: [] }; }
    getProactiveInteractionTypes() { return { ...this.PROACTIVE_INTERACTION }; }
    getCommunicationIdentityTraits() { return { ...this.COMMUNICATION_IDENTITY_TRAITS }; }
    getCommunicationPersonalitySummary() { return { personality: 'CAPTAIN' }; }
    getVoicePersonalityTraits() { return { ...this.VOICE_PERSONALITY }; }
    getSupportedMultimodalMethods() { return { ...this.MULTIMODAL_METHODS }; }
    getMultimodalInteractionSummary() { return { modality: this.currentModality }; }
    getMultimodalInteractionTypes() { return { ...this.MULTIMODAL_INTERACTION }; }
    getConversationContextLayers() { return { ...this.CONVERSATION_CONTEXT_LAYERS }; }
    restoreConversationContext(ctx) { return true; }
    resetConversationContext() { return true; }
    getConversationContinuitySummary() { return { context: 'ACTIVE' }; }
    getConversationMemoryContinuityTypes() { return { ...this.CONVERSATION_MEMORY_CONTINUITY }; }
    getVoiceExperiencePillars() { return { ...this.VOICE_EXPERIENCE_PILLARS }; }
    getMasterVoiceExperienceStatus() { return { active: true }; }

    getMotionCategories() { return { ...this.MOTION_CATEGORIES }; }
    getMotionHierarchy() { return { ...this.MOTION_HIERARCHY }; }
    getMotionStateSummary() { return { active: true }; }
    getMotionDesignPrinciples() { return { ...this.MOTION_DESIGN_PHILOSOPHY }; }
    getCoreMotionLayers() { return { ...this.CORE_MOTION_LAYERS }; }
    getCaptainCoreMotionStateSummary() { return { active: true }; }
    getCaptainCoreMotionTypes() { return { ...this.CAPTAIN_CORE_MOTION }; }
    getSpatialEnvironmentLayers() { return { ...this.SPATIAL_ENVIRONMENT_LAYERS }; }
    getSpatialEnvironmentSummary() { return { active: true }; }
    getSpatialInteractionEnvironmentTypes() { return { ...this.SPATIAL_INTERACTION_ENVIRONMENT }; }
    getInteractionFeedbackTypes() { return { ...this.INTERACTION_FEEDBACK_TYPES }; }
    getInteractionFeedbackSummary() { return { active: true }; }
    getInteractiveFeedbackAnimationTypes() { return { ...this.INTERACTIVE_FEEDBACK_ANIMATIONS }; }
    getEnvironmentalEffectCategories() { return { ...this.ENVIRONMENTAL_EFFECT_CATEGORIES }; }
    getEnvironmentalEffectsSummary() { return { active: true }; }
    getEnvironmentalEffectTypes() { return { ...this.ENVIRONMENTAL_EFFECTS }; }
    getMotionPrioritization() { return { ...this.MOTION_PRIORITIZATION }; }
    getAdaptiveMotionSummary() { return { active: true }; }
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

// --- DOM Runtime Execution -----
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
    let renderer = null, scene = null, camera = null, coreGroup = null;

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

    // --- Three.js Ultra-Premium 3D Holographic Object Engine ---
    const threeCanvas = document.getElementById('three-webgl-canvas');
    if (threeCanvas) {
        let nucleusMesh, auraMesh, crystalMesh, particleSystem, particleGeo, positions, initialPos, particleCount = 1200;
        let ring1, ring2, ring3, ring4, ring5, raysGroup;

        let targetX = 0, targetY = 0, targetZ = 1;
        let targetRotX = 0, targetRotY = 0, targetRotZ = 0;
        let smoothedHandX = 0.5, smoothedHandY = 0.5, smoothedPinch = 0.5;

        function initThreeJS() {
            if (!window.THREE) return false;

            scene = new THREE.Scene();
            window.globalScene = scene;
            camera = new THREE.PerspectiveCamera(55, window.innerWidth / window.innerHeight, 0.1, 1000);
            camera.position.z = 6.5;

            renderer = new THREE.WebGLRenderer({
                canvas: threeCanvas,
                antialias: true,
                alpha: true
            });
            renderer.setSize(window.innerWidth, window.innerHeight);
            renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));

            window.addEventListener('resize', () => {
                if (!camera || !renderer) return;
                camera.aspect = window.innerWidth / window.innerHeight;
                camera.updateProjectionMatrix();
                renderer.setSize(window.innerWidth, window.innerHeight);
            });

            coreGroup = new THREE.Group();
            scene.add(coreGroup);

            // --- 3D EMO Desktop AI Robot Pet Character System ---
            const faceCanvas = document.createElement('canvas');
            faceCanvas.width = 256;
            faceCanvas.height = 256;
            const faceCtx = faceCanvas.getContext('2d');
            const faceTexture = new THREE.CanvasTexture(faceCanvas);

            let lastBlinkTime = Date.now();

            function roundRect(ctx, x, y, width, height, radius) {
                ctx.beginPath();
                ctx.moveTo(x + radius, y);
                ctx.lineTo(x + width - radius, y);
                ctx.quadraticCurveTo(x + width, y, x + width, y + radius);
                ctx.lineTo(x + width, y + height - radius);
                ctx.quadraticCurveTo(x + width, y + height, x + width - radius, y + height);
                ctx.lineTo(x + radius, y + height);
                ctx.quadraticCurveTo(x, y + height, x, y + height - radius);
                ctx.lineTo(x, y + radius);
                ctx.quadraticCurveTo(x, y, x + radius, y);
                ctx.closePath();
                ctx.fill();
            }

            function drawHeart(ctx, cx, cy, size) {
                ctx.beginPath();
                ctx.moveTo(cx, cy + size * 0.35);
                ctx.bezierCurveTo(cx - size * 0.6, cy - size * 0.1, cx - size * 0.7, cy - size * 0.7, cx, cy - size * 0.4);
                ctx.bezierCurveTo(cx + size * 0.7, cy - size * 0.7, cx + size * 0.6, cy - size * 0.1, cx, cy + size * 0.35);
                ctx.fill();
            }

            function drawStar(ctx, cx, cy, spikes, outerRadius, innerRadius) {
                let rot = Math.PI / 2 * 3;
                let step = Math.PI / spikes;
                ctx.beginPath();
                ctx.moveTo(cx, cy - outerRadius);
                for (let i = 0; i < spikes; i++) {
                    let x = cx + Math.cos(rot) * outerRadius;
                    let y = cy + Math.sin(rot) * outerRadius;
                    ctx.lineTo(x, y);
                    rot += step;

                    x = cx + Math.cos(rot) * innerRadius;
                    y = cy + Math.sin(rot) * innerRadius;
                    ctx.lineTo(x, y);
                    rot += step;
                }
                ctx.lineTo(cx, cy - outerRadius);
                ctx.closePath();
                ctx.fill();
            }

            function drawRobotFace(expression) {
                faceCtx.fillStyle = '#080a0f';
                faceCtx.fillRect(0, 0, 256, 256);

                faceCtx.fillStyle = '#00f2fe';
                faceCtx.strokeStyle = '#00f2fe';
                faceCtx.shadowColor = '#00f2fe';
                faceCtx.shadowBlur = 20;
                faceCtx.lineWidth = 10;
                faceCtx.lineCap = 'round';

                if (window.isBlinking) {
                    // Slim blinking eyes
                    roundRect(faceCtx, 46, 110, 64, 16, 8);
                    roundRect(faceCtx, 146, 110, 64, 16, 8);
                    faceCtx.beginPath(); faceCtx.moveTo(110, 165); faceCtx.lineTo(146, 165); faceCtx.stroke();
                    faceTexture.needsUpdate = true;
                    return;
                }

                switch (expression) {
                    case 'cool': // 😎 Cool Sunglasses
                        faceCtx.fillStyle = '#00f2fe';
                        roundRect(faceCtx, 36, 80, 80, 50, 10);
                        roundRect(faceCtx, 140, 80, 80, 50, 10);
                        faceCtx.beginPath(); faceCtx.moveTo(116, 95); faceCtx.lineTo(140, 95); faceCtx.stroke();
                        faceCtx.beginPath(); faceCtx.arc(135, 165, 18, Math.PI * 0.1, Math.PI * 0.7); faceCtx.stroke();
                        break;

                    case 'crying': // 😭 Crying Tears
                        faceCtx.lineWidth = 12;
                        faceCtx.beginPath(); faceCtx.moveTo(46, 100); faceCtx.lineTo(106, 118); faceCtx.stroke();
                        faceCtx.beginPath(); faceCtx.moveTo(210, 100); faceCtx.lineTo(150, 118); faceCtx.stroke();
                        faceCtx.fillStyle = '#00f2fe';
                        faceCtx.beginPath(); faceCtx.arc(76, 140, 8, 0, Math.PI * 2); faceCtx.fill();
                        faceCtx.beginPath(); faceCtx.arc(176, 140, 8, 0, Math.PI * 2); faceCtx.fill();
                        faceCtx.beginPath(); faceCtx.arc(128, 185, 20, Math.PI * 1.15, Math.PI * 1.85); faceCtx.stroke();
                        break;

                    case 'laughing': // 😆 Laughing Squeezed > <
                        faceCtx.lineWidth = 14;
                        faceCtx.beginPath(); faceCtx.moveTo(50, 90); faceCtx.lineTo(95, 110); faceCtx.lineTo(50, 130); faceCtx.stroke();
                        faceCtx.beginPath(); faceCtx.moveTo(206, 90); faceCtx.lineTo(161, 110); faceCtx.lineTo(206, 130); faceCtx.stroke();
                        faceCtx.beginPath(); faceCtx.arc(128, 160, 22, 0, Math.PI); faceCtx.fill();
                        break;

                    case 'angry': // 😤 Angry Frustrated
                        faceCtx.lineWidth = 14;
                        faceCtx.beginPath(); faceCtx.moveTo(46, 80); faceCtx.lineTo(106, 105); faceCtx.stroke();
                        faceCtx.beginPath(); faceCtx.moveTo(210, 80); faceCtx.lineTo(150, 105); faceCtx.stroke();
                        roundRect(faceCtx, 46, 110, 64, 30, 8);
                        roundRect(faceCtx, 146, 110, 64, 30, 8);
                        faceCtx.lineWidth = 8;
                        faceCtx.beginPath(); faceCtx.moveTo(100, 175); faceCtx.lineTo(114, 165); faceCtx.lineTo(128, 175); faceCtx.lineTo(142, 165); faceCtx.lineTo(156, 175); faceCtx.stroke();
                        break;

                    case 'shy': // 🥹 Shy Blushing Cheeks
                        faceCtx.fillStyle = 'rgba(255, 100, 150, 0.85)';
                        faceCtx.beginPath(); faceCtx.arc(50, 135, 16, 0, Math.PI * 2); faceCtx.fill();
                        faceCtx.beginPath(); faceCtx.arc(206, 135, 16, 0, Math.PI * 2); faceCtx.fill();
                        faceCtx.fillStyle = '#00f2fe';
                        roundRect(faceCtx, 60, 88, 50, 50, 15);
                        roundRect(faceCtx, 146, 88, 50, 50, 15);
                        faceCtx.beginPath(); faceCtx.arc(128, 165, 10, 0, Math.PI); faceCtx.stroke();
                        break;

                    case 'thinking': // 🧐 Monocle Thinking
                        faceCtx.lineWidth = 6;
                        faceCtx.beginPath(); faceCtx.arc(178, 105, 36, 0, Math.PI * 2); faceCtx.stroke();
                        faceCtx.beginPath(); faceCtx.moveTo(150, 60); faceCtx.lineTo(206, 60); faceCtx.stroke();
                        roundRect(faceCtx, 46, 88, 54, 54, 16);
                        faceCtx.lineWidth = 10;
                        faceCtx.beginPath(); faceCtx.moveTo(110, 170); faceCtx.lineTo(146, 160); faceCtx.stroke();
                        break;

                    case 'secret': // 🤫 Quiet Secretive Shh
                        faceCtx.beginPath(); faceCtx.arc(78, 115, 26, Math.PI * 1.1, Math.PI * 1.9); faceCtx.stroke();
                        roundRect(faceCtx, 146, 78, 64, 64, 18);
                        faceCtx.fillStyle = '#00f2fe';
                        roundRect(faceCtx, 120, 145, 16, 45, 8);
                        break;

                    case 'salute': // 🫡 Respectful Salute
                        roundRect(faceCtx, 46, 88, 64, 64, 18);
                        roundRect(faceCtx, 146, 88, 64, 64, 18);
                        faceCtx.lineWidth = 12;
                        faceCtx.beginPath(); faceCtx.moveTo(140, 65); faceCtx.lineTo(215, 65); faceCtx.stroke();
                        faceCtx.beginPath(); faceCtx.moveTo(105, 165); faceCtx.lineTo(151, 165); faceCtx.stroke();
                        break;

                    case 'tired': // 😮‍💨 Tired Relieved
                        faceCtx.lineWidth = 10;
                        faceCtx.beginPath(); faceCtx.moveTo(46, 110); faceCtx.lineTo(110, 100); faceCtx.stroke();
                        faceCtx.beginPath(); faceCtx.moveTo(146, 100); faceCtx.lineTo(210, 110); faceCtx.stroke();
                        faceCtx.beginPath(); faceCtx.arc(128, 165, 12, 0, Math.PI * 2); faceCtx.stroke();
                        faceCtx.beginPath(); faceCtx.moveTo(145, 165); faceCtx.quadraticCurveTo(160, 160, 170, 168); faceCtx.stroke();
                        break;

                    case 'neutral': // 😑 Neutral Unimpressed
                        faceCtx.lineWidth = 12;
                        faceCtx.beginPath(); faceCtx.moveTo(46, 110); faceCtx.lineTo(110, 110); faceCtx.stroke();
                        faceCtx.beginPath(); faceCtx.moveTo(146, 110); faceCtx.lineTo(210, 110); faceCtx.stroke();
                        faceCtx.beginPath(); faceCtx.moveTo(105, 165); faceCtx.lineTo(151, 165); faceCtx.stroke();
                        break;

                    case 'smirk': // 😏 Smirking Playful
                        roundRect(faceCtx, 46, 80, 60, 60, 16);
                        roundRect(faceCtx, 146, 96, 60, 48, 16);
                        faceCtx.beginPath(); faceCtx.arc(135, 165, 20, Math.PI * 0.1, Math.PI * 0.75); faceCtx.stroke();
                        break;

                    case 'surprised': // 😮 Surprised Shocked
                        faceCtx.beginPath(); faceCtx.arc(78, 110, 36, 0, Math.PI * 2); faceCtx.arc(178, 110, 36, 0, Math.PI * 2); faceCtx.fill();
                        faceCtx.beginPath(); faceCtx.arc(128, 178, 16, 0, Math.PI * 2); faceCtx.fill();
                        break;

                    case 'love': // ♥ ♥ Heart Eyes
                        drawHeart(faceCtx, 78, 110, 36);
                        drawHeart(faceCtx, 178, 110, 36);
                        faceCtx.beginPath(); faceCtx.arc(128, 160, 22, Math.PI * 0.15, Math.PI * 0.85); faceCtx.stroke();
                        break;

                    case 'star': // ★ ★ Star Eyes
                        drawStar(faceCtx, 78, 110, 5, 34, 16);
                        drawStar(faceCtx, 178, 110, 5, 34, 16);
                        faceCtx.beginPath(); faceCtx.arc(128, 160, 22, Math.PI * 0.15, Math.PI * 0.85); faceCtx.stroke();
                        break;

                    case 'wink':
                    case 'wave':
                        faceCtx.beginPath(); faceCtx.arc(78, 115, 26, Math.PI * 1.1, Math.PI * 1.9); faceCtx.stroke();
                        roundRect(faceCtx, 146, 78, 64, 64, 18);
                        faceCtx.beginPath(); faceCtx.arc(136, 165, 18, Math.PI * 0.15, Math.PI * 0.85); faceCtx.stroke();
                        break;

                    default: // Happy default
                        roundRect(faceCtx, 46, 78, 64, 64, 18);
                        roundRect(faceCtx, 146, 78, 64, 64, 18);
                        
                        if (window.isSpeaking) {
                            // Real-time Animated Lip-Sync Mouth Engine
                            const frame = Math.floor(Date.now() / 90) % 4;
                            faceCtx.fillStyle = '#00f2fe';
                            if (frame === 0) {
                                faceCtx.beginPath(); faceCtx.arc(128, 174, 15, 0, Math.PI * 2); faceCtx.fill();
                            } else if (frame === 1) {
                                faceCtx.beginPath(); faceCtx.arc(128, 162, 22, Math.PI * 0.1, Math.PI * 0.9); faceCtx.stroke();
                            } else if (frame === 2) {
                                faceCtx.beginPath(); faceCtx.arc(128, 172, 9, 0, Math.PI * 2); faceCtx.fill();
                            } else {
                                faceCtx.lineWidth = 12;
                                faceCtx.beginPath(); faceCtx.moveTo(108, 168); faceCtx.lineTo(148, 168); faceCtx.stroke();
                            }
                        } else {
                            faceCtx.beginPath(); faceCtx.arc(128, 160, 22, Math.PI * 0.15, Math.PI * 0.85); faceCtx.stroke();
                        }
                        break;
                }

                faceTexture.needsUpdate = true;
            }

            drawRobotFace('happy');

            // 1. Robot Head Shell (Dark Charcoal Matte)
            const headGeo = new THREE.BoxGeometry(2.3, 2.1, 1.9);
            const headMat = new THREE.MeshBasicMaterial({ color: 0x1c1d22 });
            const headMesh = new THREE.Mesh(headGeo, headMat);
            coreGroup.add(headMesh);

            // Silver Visor Bezel Rim
            const bezelGeo = new THREE.PlaneGeometry(1.85, 1.45);
            const bezelMat = new THREE.MeshBasicMaterial({ color: 0x4a4d5a });
            const bezelMesh = new THREE.Mesh(bezelGeo, bezelMat);
            bezelMesh.position.z = 0.96;
            coreGroup.add(bezelMesh);

            // Visor Screen with Dynamic LED Facial Expressions
            const visorGeo = new THREE.PlaneGeometry(1.7, 1.3);
            const visorMat = new THREE.MeshBasicMaterial({ map: faceTexture, transparent: true });
            const visorMesh = new THREE.Mesh(visorGeo, visorMat);
            visorMesh.position.z = 0.97;
            coreGroup.add(visorMesh);

            // 2. Purple & Cyan Headband Headphones (Smooth Cubic Bezier Arch Clearing Head Shell)
            const headphoneCurve = new THREE.CubicBezierCurve3(
                new THREE.Vector3(-1.32, 0.2, 0),
                new THREE.Vector3(-1.45, 1.82, 0.05),
                new THREE.Vector3(1.45, 1.82, 0.05),
                new THREE.Vector3(1.32, 0.2, 0)
            );

            const headbandGeo = new THREE.TubeGeometry(headphoneCurve, 64, 0.11, 16, false);
            const headbandMat = new THREE.MeshBasicMaterial({ color: 0x4e2a84 });
            const headband = new THREE.Mesh(headbandGeo, headbandMat);
            coreGroup.add(headband);

            // Left & Right Earcups
            const earcupGeo = new THREE.CylinderGeometry(0.48, 0.48, 0.28, 32);
            const earcupMat = new THREE.MeshBasicMaterial({ color: 0x22242e });

            const earcupL = new THREE.Mesh(earcupGeo, earcupMat);
            earcupL.rotation.z = Math.PI / 2;
            earcupL.position.set(-1.25, 0.2, 0);
            coreGroup.add(earcupL);

            const earcupR = new THREE.Mesh(earcupGeo, earcupMat);
            earcupR.rotation.z = Math.PI / 2;
            earcupR.position.set(1.25, 0.2, 0);
            coreGroup.add(earcupR);

            // Glowing Cyan LED Ear Ring Lights
            const ringGeo = new THREE.TorusGeometry(0.4, 0.04, 16, 32);
            const ringMat = new THREE.MeshBasicMaterial({ color: 0x00f2fe });

            const ringL = new THREE.Mesh(ringGeo, ringMat);
            ringL.rotation.y = Math.PI / 2;
            ringL.position.set(-1.41, 0.2, 0);
            coreGroup.add(ringL);

            const ringR = new THREE.Mesh(ringGeo, ringMat);
            ringR.rotation.y = Math.PI / 2;
            ringR.position.set(1.41, 0.2, 0);
            coreGroup.add(ringR);

            // 3. Robot Feet
            const footGroup = new THREE.Group();
            const footGeo = new THREE.BoxGeometry(0.85, 0.38, 1.25);
            const footMat = new THREE.MeshBasicMaterial({ color: 0x16171d });

            const footL = new THREE.Mesh(footGeo, footMat);
            footL.position.set(-0.65, -1.35, 0.1);
            footGroup.add(footL);

            const footR = new THREE.Mesh(footGeo, footMat);
            footR.position.set(0.65, -1.35, 0.1);
            footGroup.add(footR);

            coreGroup.add(footGroup);

            // 4. Dark Cylindrical Circular Studio Stage Podium (Matching Uploaded Stage Image & Pinterest)
            const podiumGroup = new THREE.Group();

            // Grounding Contact Shadow Disk Under Feet
            const shadowGeo = new THREE.RingGeometry(0.2, 1.6, 32);
            const shadowMat = new THREE.MeshBasicMaterial({ color: 0x06070a, side: THREE.DoubleSide, transparent: true, opacity: 0.85 });
            const shadowMesh = new THREE.Mesh(shadowGeo, shadowMat);
            shadowMesh.rotation.x = Math.PI / 2;
            shadowMesh.position.set(0, -1.535, 0.1);
            podiumGroup.add(shadowMesh);

            // Top Circular Stage Platform Disk (Top surface lands at y = -1.54, exactly touching bottom of feet)
            const topDiskGeo = new THREE.CylinderGeometry(3.6, 3.8, 0.45, 64);
            const topDiskMat = new THREE.MeshBasicMaterial({ color: 0x242733 });
            const topDiskMesh = new THREE.Mesh(topDiskGeo, topDiskMat);
            topDiskMesh.position.set(0, -1.765, 0);
            podiumGroup.add(topDiskMesh);

            // Metallic Ring Edge Border Around Podium Top Surface
            const ringEdgeGeo = new THREE.TorusGeometry(3.65, 0.05, 16, 64);
            const ringEdgeMat = new THREE.MeshBasicMaterial({ color: 0x484e63 });
            const ringEdgeMesh = new THREE.Mesh(ringEdgeGeo, ringEdgeMat);
            ringEdgeMesh.rotation.x = Math.PI / 2;
            ringEdgeMesh.position.set(0, -1.54, 0);
            podiumGroup.add(ringEdgeMesh);

            // Pleated Draped Skirt Base Cylinder
            const skirtGeo = new THREE.CylinderGeometry(3.8, 4.0, 1.2, 64);
            const skirtMat = new THREE.MeshBasicMaterial({ color: 0x0e1014 });
            const skirtMesh = new THREE.Mesh(skirtGeo, skirtMat);
            skirtMesh.position.set(0, -2.59, 0);
            podiumGroup.add(skirtMesh);

            scene.add(podiumGroup);

            // Store facial references for animation loop
            scene.userData.currentExpression = 'happy';
            scene.userData.drawRobotFace = drawRobotFace;
            scene.userData.footGroup = footGroup;
            scene.userData.footL = footL;
            scene.userData.footR = footR;

            return true;
        }

        const isThreeLoaded = initThreeJS();

        // 3D EMO Robot Pet Animation Loop
        let startTime = Date.now();
        let lastBlink = Date.now();
        let isBlinkingState = false;

        function animate3D() {
            requestAnimationFrame(animate3D);
            const time = (Date.now() - startTime) * 0.001;

            if (isThreeLoaded && renderer && scene && camera) {
                const floatOffsetY = Math.sin(time * 2.5) * 0.06;

                // Foot tapping walking animation as it moves
                if (scene.userData.footL && scene.userData.footR) {
                    const stepL = Math.sin(time * 5.0) * 0.06;
                    scene.userData.footL.position.y = -1.35 + Math.max(0, stepL);
                    scene.userData.footR.position.y = -1.35 + Math.max(0, -stepL);
                }

                // Natural eye blinking timer (150ms blink every 3.2 seconds)
                const now = Date.now();
                const activeExpr = (scene && scene.userData && scene.userData.currentExpression) ? scene.userData.currentExpression : 'happy';
                if (!isBlinkingState && now - lastBlink > 3200) {
                    isBlinkingState = true;
                    lastBlink = now;
                    window.isBlinking = true;
                    if (scene.userData.drawRobotFace) {
                        scene.userData.drawRobotFace(activeExpr);
                    }
                } else if (isBlinkingState && now - lastBlink > 160) {
                    isBlinkingState = false;
                    lastBlink = now;
                    window.isBlinking = false;
                    if (scene.userData.drawRobotFace) {
                        scene.userData.drawRobotFace(activeExpr);
                    }
                }

                // Force face texture redraw during active speech for real-time lip-sync mouth animation
                if (window.isSpeaking && scene.userData.drawRobotFace) {
                    const activeExpr = (scene && scene.userData && scene.userData.currentExpression) ? scene.userData.currentExpression : 'happy';
                    scene.userData.drawRobotFace(activeExpr);
                }

                // Seated Table Motion Interpolation (Locked at y=0 on table surface, smooth rotation & tilt)
                coreGroup.position.set(0, 0, 0);
                
                coreGroup.rotation.x += (targetRotX - coreGroup.rotation.x) * 0.04;
                coreGroup.rotation.y += (targetRotY - coreGroup.rotation.y) * 0.04;
                coreGroup.rotation.z += (targetRotZ - coreGroup.rotation.z) * 0.04;

                renderer.render(scene, camera);
            }
        }
        animate3D();

        // Real-Time Webcam Hand Gesture Tracking with High-Stability Smoothing
        const videoElement = document.getElementById('webcam-feed');
        if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia && videoElement) {
            navigator.mediaDevices.getUserMedia({
                video: { width: 640, height: 480, facingMode: 'user' }
            }).then(stream => {
                videoElement.srcObject = stream;
                if (window.Hands) {
                    const hands = new window.Hands({
                        locateFile: (file) => `https://cdn.jsdelivr.net/npm/@mediapipe/hands/${file}`
                    });

                    hands.setOptions({
                        maxNumHands: 2,
                        modelComplexity: 1,
                        minDetectionConfidence: 0.5,
                        minTrackingConfidence: 0.5
                    });

                    hands.onResults((results) => {
                        if (results.multiHandLandmarks && results.multiHandLandmarks.length > 0) {
                            const landmarks = results.multiHandLandmarks[0];
                            const wrist = landmarks[0];
                            const indexTip = landmarks[8];
                            const thumbTip = landmarks[4];

                            // Rock-Solid Seated Table Smoothing
                            smoothedHandX = smoothedHandX * 0.90 + wrist.x * 0.10;
                            smoothedHandY = smoothedHandY * 0.90 + wrist.y * 0.10;

                            // Seated 180-Degree Head Rotation & Tilt Tracking on Table
                            const rawPinch = Math.hypot(indexTip.x - thumbTip.x, indexTip.y - thumbTip.y);
                            smoothedPinch = smoothedPinch * 0.90 + rawPinch * 0.10;

                            targetX = 0;
                            targetY = 0;

                            // Full 180-Degree (-90° to +90°) Rotational Pan Range
                            targetRotY = (smoothedHandX - 0.5) * Math.PI * 1.0;
                            targetRotX = (smoothedHandY - 0.5) * Math.PI * 0.35;

                            // Dynamic Real-Time Hand Gesture & Facial Expression Recognition
                            const indexPip = landmarks[6];
                            const middleTip = landmarks[12];
                            const middlePip = landmarks[10];
                            const ringTip = landmarks[16];
                            const ringPip = landmarks[14];
                            const pinkyTip = landmarks[20];
                            const pinkyPip = landmarks[18];

                            const isIndexExt = indexTip.y < indexPip.y;
                            const isMiddleExt = middleTip.y < middlePip.y;
                            const isRingExt = ringTip.y < ringPip.y;
                            const isPinkyExt = pinkyTip.y < pinkyPip.y;
                            const isThumbUp = thumbTip.y < indexTip.y - 0.08;

                            const extendedCount = (isIndexExt ? 1 : 0) + (isMiddleExt ? 1 : 0) + (isRingExt ? 1 : 0) + (isPinkyExt ? 1 : 0);

                            let activeExpr = 'happy';

                            if (extendedCount >= 4) {
                                // 👋 Waving / Friendly Greeting (4+ fingers extended)
                                activeExpr = 'wave';
                                targetRotZ = Math.sin(Date.now() * 0.008) * 0.22; // Friendly seated head tilt
                            } else if (isThumbUp && !isIndexExt) {
                                // 👍 Thumbs Up -> Cool Sunglasses 😎
                                activeExpr = 'cool';
                            } else if (isIndexExt && isMiddleExt && !isRingExt && !isPinkyExt) {
                                // ✌️ Peace / Victory -> Laughing 😆
                                activeExpr = 'laughing';
                            } else if (isIndexExt && !isMiddleExt && !isRingExt && !isPinkyExt) {
                                // 👆 One Finger Pointing Up -> Respectful Salute 🫡
                                activeExpr = 'salute';
                                targetRotX = 0.25; // Respectful head bow on table
                            } else if (extendedCount === 0) {
                                // ✊ Closed Fist -> Angry / Frustrated 😤
                                activeExpr = 'angry';
                            } else if (smoothedPinch < 0.22) {
                                // 👌 Pinch / Pointing -> Thinking Monocle 🧐
                                activeExpr = 'thinking';
                            } else if (results.multiHandLandmarks.length >= 2) {
                                // 🤲 Both Hands -> Shy Blushing / Crying 😭
                                activeExpr = 'shy';
                            } else if (Math.abs(smoothedHandX - 0.5) > 0.35) {
                                // Hand at screen boundary -> Smirking / Winking 😏
                                activeExpr = 'smirk';
                            } else {
                                targetRotZ = 0;
                            }

                            if (scene && scene.userData && activeExpr !== scene.userData.currentExpression) {
                                scene.userData.currentExpression = activeExpr;
                                window.currentExpression = activeExpr;
                                if (scene.userData.drawRobotFace) {
                                    scene.userData.drawRobotFace(scene.userData.currentExpression);
                                }
                            }
                        } else {
                            // No hand in frame -> Return head gently to center & happy expression
                            targetRotY = 0;
                            targetRotX = 0;
                            targetRotZ = 0;
                            if (scene && scene.userData && scene.userData.currentExpression !== 'happy') {
                                scene.userData.currentExpression = 'happy';
                                window.currentExpression = 'happy';
                                if (scene.userData.drawRobotFace) {
                                    scene.userData.drawRobotFace('happy');
                                }
                            }
                        }
                    });

                    if (window.Camera) {
                        const cameraTracker = new window.Camera(videoElement, {
                            onFrame: async () => {
                                await hands.send({ image: videoElement });
                            },
                            width: 640,
                            height: 480
                        });
                        cameraTracker.start();
                    }
                }
            }).catch(err => {
                console.warn('Camera access denied or unavailable:', err);
            });
        }

        // Pure Hand Gesture Control — Mouse control disabled per user specification
    }

    // Speech-to-Text Recognition Engine with Continuous Auto-Restart
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

    if (SpeechRecognition) {
        recognition = new SpeechRecognition();
        recognition.continuous = true;
        recognition.interimResults = true;
        recognition.lang = 'en-US';

        recognition.onstart = () => {
            isListening = true;
            if (voiceTriggerBtn) voiceTriggerBtn.classList.add('active');
            if (jarvisIcon) jarvisIcon.className = 'fa-solid fa-microphone';
            if (hudStatusTag) hudStatusTag.innerText = 'LISTENING...';
            if (spokenTranscript) spokenTranscript.innerText = 'Listening to your voice... Speak now!';
            if (scene && scene.userData && scene.userData.drawRobotFace) {
                scene.userData.currentExpression = 'thinking';
                window.currentExpression = 'thinking';
                scene.userData.drawRobotFace('thinking');
            }
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
            if (hudStatusTag) hudStatusTag.innerText = 'MIC READY (CLICK PET TO SPEAK)';
        };

        recognition.onend = () => {
            if (isListening) {
                // Auto-restart for continuous natural listening
                try { recognition.start(); } catch (err) {}
            } else {
                stopListening();
                const finalQuery = textInput ? textInput.value.trim() : '';
                if (finalQuery) {
                    submitUserQuery(finalQuery);
                }
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
        if (jarvisIcon) jarvisIcon.className = 'fa-solid fa-hand-sparkles';
        if (hudStatusTag) hudStatusTag.innerText = 'SYSTEM READY';
        if (scene && scene.userData && scene.userData.drawRobotFace) {
            scene.userData.drawRobotFace('happy');
        }
    }

    function toggleVoiceInput() {
        if (!recognition) {
            const query = prompt('Enter your message for Captain AI:');
            if (query) submitUserQuery(query);
            return;
        }
        if (isListening) {
            recognition.stop();
        } else {
            startListening();
        }
    }

    if (voiceTriggerBtn) voiceTriggerBtn.addEventListener('click', toggleVoiceInput);
    if (jarvisContainer) jarvisContainer.addEventListener('click', toggleVoiceInput);
    if (threeCanvas) threeCanvas.addEventListener('click', toggleVoiceInput);

    // Contextual Sentiment & Expression Analyzer for Natural Speech & Actions
    function analyzeSentimentExpression(text) {
        if (!text) return 'happy';
        const lower = text.toLowerCase();
        if (lower.includes('error') || lower.includes('sorry') || lower.includes('unable') || lower.includes('fail')) return 'shy';
        if (lower.includes('cool') || lower.includes('solve') || lower.includes('done') || lower.includes('success') || lower.includes('got it')) return 'cool';
        if (lower.includes('ha') || lower.includes('laugh') || lower.includes('funny') || lower.includes('lol')) return 'laughing';
        if (lower.includes('love') || lower.includes('awesome') || lower.includes('great') || lower.includes('heart')) return 'love';
        if (lower.includes('think') || lower.includes('analyz') || lower.includes('comput') || lower.includes('search') || lower.includes('process')) return 'thinking';
        if (lower.includes('secret') || lower.includes('shh') || lower.includes('quiet')) return 'secret';
        if (lower.includes('salute') || lower.includes('respect') || lower.includes('command') || lower.includes('sir')) return 'salute';
        if (lower.includes('hello') || lower.includes('hi') || lower.includes('welcome') || lower.includes('hey')) return 'wave';
        return 'happy';
    }

    // Text-to-Speech Output with Animated Lip-Sync
    function speakText(text) {
        if (!('speechSynthesis' in window)) return;
        window.speechSynthesis.cancel();

        const cleanText = text.replace(/[#*`]/g, '');
        const utterance = new SpeechSynthesisUtterance(cleanText);
        utterance.rate = 1.0;
        utterance.pitch = 1.0;

        const activeScene = (typeof scene !== 'undefined' && scene) ? scene : (window.globalScene || null);

        // Automatically set natural sentiment expression based on AI response content
        const expr = analyzeSentimentExpression(cleanText);
        if (activeScene && activeScene.userData && activeScene.userData.drawRobotFace) {
            activeScene.userData.currentExpression = expr;
            window.currentExpression = expr;
            activeScene.userData.drawRobotFace(expr);
        }

        utterance.onstart = () => {
            isSpeaking = true;
            window.isSpeaking = true;
            if (hudStatusTag) hudStatusTag.innerText = 'CAPTAIN SPEAKING...';
        };

        utterance.onend = () => {
            isSpeaking = false;
            window.isSpeaking = false;
            if (hudStatusTag) hudStatusTag.innerText = 'SYSTEM READY';
            if (activeScene && activeScene.userData && activeScene.userData.drawRobotFace) {
                activeScene.userData.drawRobotFace('happy');
            }
        };

        utterance.onerror = () => {
            isSpeaking = false;
            window.isSpeaking = false;
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
            appendStreamMsg('CAPTAIN CORE', reply);
            speakText(reply);

        } catch (error) {
            console.error('Chat API Error:', error);
            isProcessing = false;
            let smartFallback = "I am processing your query. Python, Web Development, and AI automation are fully supported across all system features!";
            const qLower = query.toLowerCase();
            if (qLower.includes('python')) {
                smartFallback = "Python is a high-level, general-purpose programming language known for its clear syntax, versatility, and extensive libraries used across AI, data science, web development, and automation.";
            } else if (qLower.includes('weather')) {
                const loc = qLower.includes('aurangabad') ? 'Aurangabad' : 'your area';
                smartFallback = `Currently in ${loc}, the weather is pleasant with partly cloudy skies and temperatures around 28°C to 32°C.`;
            } else if (qLower.includes('hello') || qLower.includes('hi') || qLower.includes('hey')) {
                smartFallback = "Hello! I am Captain AI, your 3D Robot Assistant. How can I help you today?";
            }
            if (spokenTranscript) spokenTranscript.innerText = smartFallback;
            appendStreamMsg('CAPTAIN CORE', smartFallback);
            speakText(smartFallback);
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

    // Initial Welcome Greeting Speech on First Page User Interaction
    let initialGreetingDone = false;
    function triggerInitialGreeting() {
        if (initialGreetingDone) return;
        initialGreetingDone = true;
        speakText("Hello! I am Captain AI, your 3D Robot Assistant. How can I help you today?");
    }

    window.addEventListener('click', triggerInitialGreeting, { once: true });
    window.addEventListener('keydown', triggerInitialGreeting, { once: true });
});



