BGLOP_EOF         EQU         000000000h
BGLOP_LOGOL       EQU         000000001h
BGLOP_NOOP        EQU         000000002h
BGLOP_CASE        EQU         000000003h
BGLOP_DEBUG       EQU         000000004h
BGLOP_SURFACE           EQU         000000005h
BGLOP_SPNT        EQU         000000006h
BGLOP_CPNT        EQU         000000007h
BGLOP_CLOSURE           EQU         000000008h
BGLOP_GSURF       EQU         000000009h
BGLOP_GSPNT       EQU         00000000ah
BGLOP_GCPNT       EQU         00000000bh
BGLOP_GCLOSURE          EQU         00000000ch
BGLOP_JUMP        EQU         00000000dh
BGLOP_DEFRES            EQU         00000000eh
BGLOP_STRRES            EQU         00000000fh
BGLOP_CNTRES            EQU         000000010h
BGLOP_GDEFRES           EQU         000000011h
BGLOP_GSTRRES           EQU         000000012h
BGLOP_GCNTRES           EQU         000000013h
BGLOP_SETCOLOR          EQU         000000014h
BGLOP_ELEVATION_MAP           EQU         000000015h
BGLOP_DBG_DEBUG         EQU         000000016h
BGLOP_TEXTURE_ENABLE          EQU         000000017h
BGLOP_TEXTURE           EQU         000000018h
BGLOP_PALETTE           EQU         000000019h
BGLOP_RESLIST           EQU         00000001ah
BGLOP_IFIN_BOX_PLANE          EQU         00000001bh
BGLOP_IFIN2       EQU         00000001ch
BGLOP_FACE        EQU         00000001dh
BGLOP_HAZE        EQU         00000001eh
BGLOP_HORIZON           EQU         00000001fh
BGLOP_TAXI_MARKINGS           EQU         00000001fh
BGLOP_FACET_TMAP        EQU         000000020h
BGLOP_FACET4_TMAP       EQU         000000020h
BGLOP_IFIN3       EQU         000000021h
BGLOP_RETURN            EQU         000000022h
BGLOP_CALL        EQU         000000023h
BGLOP_IFIN1       EQU         000000024h
BGLOP_SEPARATION_PLANE        EQU         000000025h
BGLOP_SETWRD            EQU         000000026h
BGLOP_TEXTURED_FACET          EQU         000000027h
BGLOP_BALL        EQU         000000028h
BGLOP_GRESLIST          EQU         000000029h
BGLOP_GFACETN           EQU         00000002ah
BGLOP_ADDOBJ_32         EQU         00000002bh
BGLOP_REJECT            EQU         00000002ch
BGLOP_SCOLOR24          EQU         00000002dh
BGLOP_LCOLOR24          EQU         00000002eh
BGLOP_NEW_SCALE         EQU         00000002fh
BGLOP_BRIGHTNESS        EQU         000000030h
BGLOP_RESROW            EQU         000000031h
BGLOP_ADDOBJ            EQU         000000032h
BGLOP_INSTANCE_CALL           EQU         000000033h
BGLOP_SUPER_SCALE       EQU         000000034h
BGLOP_PNTROW            EQU         000000035h
BGLOP_PNTROWM           EQU         000000036h
BGLOP_PNT         EQU         000000037h
BGLOP_CONCAVE           EQU         000000038h
BGLOP_IFMASK            EQU         000000039h
BGLOP_VPOSITION         EQU         00000003ah
BGLOP_VINSTANCE_CALL          EQU         00000003bh
BGLOP_POSITION          EQU         00000003ch
BGLOP_SEED        EQU         00000003dh
BGLOP_FACET       EQU         00000003eh
BGLOP_SHADOW_CALL       EQU         00000003fh
BGLOP_SHADOW_VPOSITION        EQU         000000040h
BGLOP_SHADOW_VICALL           EQU         000000041h
BGLOP_POLYGON_RUNWAY          EQU         000000042h
BGLOP_NEW_TEXTURE       EQU         000000043h
BGLOP_TEXTURE_RUNWAY          EQU         000000044h
BGLOP_STROBEROW         EQU         000000045h
BGLOP_POINT_VICALL            EQU         000000046h
BGLOP_MAP_SCALE         EQU         000000047h
BGLOP_VAR_SEG           EQU         000000048h
BGLOP_BUILDING          EQU         000000049h
BGLOP_LANDING_LIGHTS          EQU         00000004ah
BGLOP_BAO_LIBRARY       EQU         00000004bh
BGLOP_VSCALE            EQU         00000004ch
BGLOP_VAR2LOW64K        EQU         00000004dh
BGLOP_LOW64K2VAR        EQU         00000004eh
BGLOP_MOVWRD            EQU         00000004fh
BGLOP_GCOLOR            EQU         000000050h
BGLOP_LCOLOR            EQU         000000051h
BGLOP_SCOLOR            EQU         000000052h
BGLOP_GCOLOR_ABS        EQU         000000053h
BGLOP_ASMCALL           EQU         000000054h
BGLOP_SURFACE_TYPE            EQU         000000055h
BGLOP_SET_WEATHER       EQU         000000056h
BGLOP_WEATHER           EQU         000000057h
BGLOP_TEXTURE_BOUNDS          EQU         000000058h
BGLOP_VAR_SEG_ID        EQU         000000059h
BGLOP_SEED_ADDOBJ       EQU         00000005ah
BGLOP_INDIRECT_CALL           EQU         00000005bh
BGLOP_FAR_CALL          EQU         00000005ch
BGLOP_TEXTURE_REPEAT          EQU         00000005dh
BGLOP_TEXTURE_ROTATE          EQU         00000005eh
BGLOP_IFSIZEV           EQU         00000005fh
BGLOP_FACE_TMAP         EQU         000000060h
BGLOP_RESLIST_SCALE           EQU         000000061h
BGLOP_IFVIS       EQU         000000062h
BGLOP_LIBRARY           EQU         000000063h
BGLOP_LIST        EQU         000000064h
BGLOP_VSCOLOR           EQU         000000065h
BGLOP_VGCOLOR           EQU         000000066h
BGLOP_VLCOLOR           EQU         000000067h
BGLOP_TMAP_LIGHT_SHADE        EQU         000000068h
BGLOP_ROAD_START        EQU         000000069h
BGLOP_ROAD_CONT         EQU         00000006ah
BGLOP_RIVER_START       EQU         00000006bh
BGLOP_RIVER_CONT        EQU         00000006ch
BGLOP_IFSIZEH           EQU         00000006dh
BGLOP_TAXIWAY_START           EQU         00000006eh
BGLOP_TAXIWAY_CONT            EQU         00000006fh
BGLOP_AREA_SENSE        EQU         000000070h
BGLOP_ALTITUDE_SET            EQU         000000071h
BGLOP_APPROACH_LIGHTS         EQU         000000072h
BGLOP_IFINBOXP          EQU         000000073h
BGLOP_ADD_CATEGORY            EQU         000000074h
BGLOP_ADD_MOUNTAIN            EQU         000000075h
BGLOP_BGL         EQU         000000076h
BGLOP_SCALE_AGL         EQU         000000077h
BGLOP_ROAD_CONTW        EQU         000000078h
BGLOP_RIVER_CONTW       EQU         000000079h
BGLOP_GFACET_TMAP       EQU         00000007ah
BGLOP_GFACE_TMAP        EQU         00000007bh
BGLOP_SELECT            EQU         00000007ch
BGLOP_PERSPECTIVE       EQU         00000007dh
BGLOP_SETWORD_LOW64K          EQU         00000007eh
BGLOP_CITY        EQU         00000007fh
BGLOP_RESPNT            EQU         000000080h
BGLOP_ANTI_ALIAS        EQU         000000081h
BGLOP_SHADOW_POSITION         EQU         000000082h
BGLOP_RESCALE           EQU         000000083h
BGLOP_SURFACE_NORMAL          EQU         000000084h
BGLOP_ASD_NAME          EQU         000000085h
BGLOP_NOOP3       EQU         000000086h
BGLOP_FIXED_COLORS            EQU         000000087h
BGLOP_JUMP_32           EQU         000000088h
BGLOP_VAR_BASE_32       EQU         000000089h
BGLOP_CALL_32           EQU         00000008ah
BGLOP_ADDCAT_32         EQU         00000008bh
BGLOP_ASM_CALL_32       EQU         00000008ch
BGLOP_FILE_MARKER_32          EQU         00000008dh
BGLOP_VFILE_MARKER            EQU         00000008eh
BGLOP_ALPHA       EQU         00000008fh
BGLOP_TRIANGLE_FAN            EQU         000000090h
BGLOP_TEXT        EQU         000000091h
BGLOP_MIPMAP            EQU         000000092h
BGLOP_SPECULAR          EQU         000000093h
BGLOP_CRASH       EQU         000000094h
BGLOP_CRASH_INDIRECT          EQU         000000095h
BGLOP_CRASH_START       EQU         000000096h
BGLOP_CRASH_SPHERE            EQU         000000097h
BGLOP_CRASH_BOX         EQU         000000098h
BGLOP_SET_CRASH         EQU         000000099h
BGLOP_TILED_ELEVATION_MAP           EQU         00000009ah
BGLOP_VRESLIST          EQU         00000009bh
BGLOP_VLIBRARY_CALL           EQU         00000009ch
BGLOP_VSCALEV           EQU         00000009dh
BGLOP_INTERPOLATE       EQU         00000009eh
BGLOP_OVERRIDE          EQU         00000009fh
BGLOP_NEW_BUILDING            EQU         0000000a0h
BGLOP_GENERIC_OBJECT          EQU         0000000a0h
BGLOP_SET_CLASSIFICATION_LIST_ENTRY       EQU         0000000a1h
BGLOP_SET_CURRENT_VARIATION_TEXTURE_LIST        EQU         0000000a2h
BGLOP_TILED_CLASSIFICATION_ELEVATION_MAP        EQU         0000000a3h
BGLOP_VALPHA            EQU         0000000a4h
BGLOP_SET_CURRENT_VARIATION_FROM_CLASSIFICATION       EQU         0000000a5h
BGLOP_TARGET_INDICATOR        EQU         0000000a6h
BGLOP_SPRITE_VICALL           EQU         0000000a7h
BGLOP_TEXTURED_ROAD           EQU         0000000a8h
BGLOP_IFIN_INSTANCED_BOX_PLANE            EQU         0000000a9h
BGLOP_NEW_RUNWAY        EQU         0000000aah
BGLOP_OBJECT_MARKER           EQU         0000000abh
BGLOP_ZBIAS       EQU         0000000ach
BGLOP_ANIMATE           EQU         0000000adh
BGLOP_TRANSFORM_END           EQU         0000000aeh
BGLOP_TRANSFORM_MAT           EQU         0000000afh
BGLOP_CRASH_OCTTREE           EQU         0000000b0h
BGLOP_TAG         EQU         0000000b1h
BGLOP_LIGHT       EQU         0000000b2h
BGLOP_IFINF1            EQU         0000000b3h
BGLOP_TEXTURE_SIZE            EQU         0000000b4h
BGLOP_VERTEX_LIST       EQU         0000000b5h
BGLOP_MATERIAL_LIST           EQU         0000000b6h
BGLOP_TEXTURE_LIST            EQU         0000000b7h
BGLOP_SET_MATERIAL            EQU         0000000b8h
BGLOP_DRAW_TRILIST            EQU         0000000b9h
BGLOP_DRAW_LINELIST           EQU         0000000bah
BGLOP_DRAW_POINTLIST          EQU         0000000bbh
BGLOP_BEGIN       EQU         0000000bch
BGLOP_END         EQU         0000000bdh
BGLOP_TAXIWAY_SIGN_LIST       EQU         0000000beh
BGLOP_MOUSERECT_LIST          EQU         0000000bfh
BGLOP_SET_MOUSERECT           EQU         0000000c0h
BGLOP_SET_MATERIAL_ANIMATE          EQU         0000000c1h
BGLOP_MODWORD           EQU         0000000c2h
BGLOP_ANIMATE_INDIRECT        EQU         0000000c3h
BGLOP_SET_MATRIX_INDIRECT           EQU         0000000c4h
BGLOP_POINTVI_INDIRECT        EQU         0000000c5h
BGLOP_TRANSFORM_INDIRECT            EQU         0000000c6h
BGLOP_MAX         EQU         0000000c6h
BGLOP_MAC         EQU         0000000c7h
BGL_DATA_CLASS_UNKNOWN        EQU         0t
BGL_DATA_CLASS_DIRECT_QMID          EQU         1t
BGL_DATA_CLASS_INDIRECT_QMID        EQU         2t
BGL_DATA_CLASS_AIRPORT_NAME_INDEX         EQU         3t
BGL_DATA_CLASS_ICAO_INDEX           EQU         4t
BGL_DATA_CLASS_GUID_INDEX           EQU         5t
BGL_DATA_CLASS_EXCLUSION            EQU         6t
BGL_DATA_CLASS_TIME_ZONE            EQU         7t
 
BGL_DATA_CLASS          TYPEDEF           SDWORD
 
PBGL_DATA_CLASS         TYPEDEF           PTR SDWORD
 
PPBGL_DATA_CLASS        TYPEDEF           PTR PTR SDWORD
 
BGL_DATA_TYPE_NONE            EQU         0t
BGL_DATA_TYPE_COPYRIGHT       EQU         1t
BGL_DATA_TYPE_GUID            EQU         2t
BGL_DATA_TYPE_AIRPORT         EQU         3t
BGL_DATA_TYPE_NAV       EQU         19t
BGL_DATA_TYPE_NDB       EQU         23t
BGL_DATA_TYPE_MARKER          EQU         24t
BGL_DATA_TYPE_BOUNDARY        EQU         32t
BGL_DATA_TYPE_WAYPOINT        EQU         34t
BGL_DATA_TYPE_GEOPOL          EQU         35t
BGL_DATA_TYPE_SCENERY_OBJECT        EQU         37t
BGL_DATA_TYPE_AIRPORT_NAME_INDEX          EQU         39t
BGL_DATA_TYPE_VOR_ICAO_INDEX        EQU         40t
BGL_DATA_TYPE_NDB_ICAO_INDEX        EQU         41t
BGL_DATA_TYPE_WAYPOINT_ICAO_INDEX         EQU         42t
BGL_DATA_TYPE_MODEL_DATA            EQU         43t
BGL_DATA_TYPE_AIRPORT_SUMMARY       EQU         44t
BGL_DATA_TYPE_EXCLUSION       EQU         46t
BGL_DATA_TYPE_TIME_ZONE       EQU         47t
BGL_DATA_TYPE_FAKE_TYPES            EQU         10000t
BGL_DATA_TYPE_ICAO_RUNWAY           EQU         10001t
 
BGL_DATA_TYPE           TYPEDEF           SDWORD
 
PBGL_DATA_TYPE          TYPEDEF           PTR SDWORD
 
PPBGL_DATA_TYPE         TYPEDEF           PTR PTR SDWORD
 
RUNWAY_SUBOP_BASE       EQU         000000001h
RUNWAY_SUBOP_BASE_THRESHOLD         EQU         000000002h
RUNWAY_SUBOP_RECIP_THRESHOLD        EQU         000000003h
RUNWAY_SUBOP_BASE_BLAST_PAD         EQU         000000004h
RUNWAY_SUBOP_RECIP_BLAST_PAD        EQU         000000005h
RUNWAY_SUBOP_BASE_APPROACH          EQU         000000006h
RUNWAY_SUBOP_RECIP_APPROACH         EQU         000000007h
RUNWAY_SUBOP_BASE_OVERRUN           EQU         000000008h
RUNWAY_SUBOP_RECIP_OVERRUN          EQU         000000009h
RUNWAY_SUBOP_BASE_DISTANCE          EQU         00000000ah
RUNWAY_SUBOP_RECIP_DISTANCE         EQU         00000000bh
RUNWAY_EDGES_BIT        TEXTEQU           <BIT0>
RUNWAY_THRESHOLD_BIT          TEXTEQU           <BIT1>
RUNWAY_TOUCHDOWN_BIT          TEXTEQU           <BIT2>
RUNWAY_FIXED_BIT        TEXTEQU           <BIT3>
RUNWAY_DASHES_BIT       TEXTEQU           <BIT4>
RUNWAY_IDENT_BIT        TEXTEQU           <BIT5>
RUNWAY_PRECISION_BIT          TEXTEQU           <BIT6>
RUNWAY_EDGE_PAVEMENT_BIT            TEXTEQU           <BIT7>
RUNWAY_EDGES_MASK       TEXTEQU           <~RUNWAY_EDGES_BIT>
RUNWAY_THRESHOLD_MASK         TEXTEQU           <~RUNWAY_THRESHOLD_BIT>
RUNWAY_TOUCHDOWN_MASK         TEXTEQU           <~RUNWAY_TOUCHDOWN_BIT>
RUNWAY_FIXED_MASK       TEXTEQU           <~RUNWAY_FIXED_BIT>
RUNWAY_DASHES_MASK            TEXTEQU           <~RUNWAY_DASHES_BIT>
RUNWAY_IDENT_MASK       TEXTEQU           <~RUNWAY_IDENT_BIT>
RUNWAY_PRECISION_MASK         TEXTEQU           <~RUNWAY_PRECISION_BIT>
RUNWAY_EDGE_PAVEMENT_MASK           TEXTEQU           <~RUNWAY_EDGE_PAVEMENT_BIT>
RUNWAY_APPROACH_END_BIT       TEXTEQU           <BIT0>
RUNWAY_APPROACH_UNK_BIT       TEXTEQU           <BIT1>
RUNWAY_APPROACH_REIL_BIT            TEXTEQU           <BIT2>
RUNWAY_APPROACH_VASI_BIT            TEXTEQU           <BIT3>
RUNWAY_APPROACH_LDIN_BIT            TEXTEQU           <BIT4>
RUNWAY_APPROACH_SYSTEM_BIT          TEXTEQU           <BIT5>
RUNWAY_APPROACH_TOUCHDOWN_BIT       TEXTEQU           <BIT6>
RUNWAY_APPROACH_END_MASK            TEXTEQU           <~RUNWAY_APPROACH_END_BIT>
RUNWAY_APPROACH_UNK_MASK            TEXTEQU           <~RUNWAY_APPROACH_UNK_BIT>
RUNWAY_APPROACH_REIL_MASK           TEXTEQU           <~RUNWAY_APPROACH_REIL_BIT>
RUNWAY_APPROACH_VASI_MASK           TEXTEQU           <~RUNWAY_APPROACH_VASI_BIT>
RUNWAY_APPROACH_LDIN_MASK           TEXTEQU           <~RUNWAY_APPROACH_LDIN_BIT>
RUNWAY_APPROACH_SYSTEM_MASK         TEXTEQU           <~RUNWAY_APPROACH_SYSTEM_BIT>
RUNWAY_APPROACH_TOUCHDOWN_MASK            TEXTEQU           <~RUNWAY_APPROACH_TOUCHDOWN_BIT>
VASI_TYPE_NONE          EQU         0t
VASI_TYPE_2_1           EQU         1t
VASI_TYPE_3_1           EQU         2t
VASI_TYPE_2_2           EQU         3t
VASI_TYPE_3_2           EQU         4t
VASI_TYPE_2_3           EQU         5t
VASI_TYPE_3_3           EQU         6t
VASI_TYPE_PAPI_2        EQU         7t
VASI_TYPE_PAPI_4        EQU         8t
VASI_TYPE_TRI_COLOR           EQU         9t
VASI_TYPE_PVASI         EQU         10t
VASI_TYPE_TVASI         EQU         11t
VASI_TYPE_BALL          EQU         12t
VASI_TYPE_PANELS        EQU         13t
VASI_TYPE_MAX           EQU         14t
 
VASI_TYPE         TYPEDEF           SDWORD
 
PVASI_TYPE        TYPEDEF           PTR SDWORD
 
PPVASI_TYPE       TYPEDEF           PTR PTR SDWORD
 
TAXI_SUBOPF_BIT         EQU         000000080h
TAXI_SUBOPF_MASK        TEXTEQU           <~TAXI_SUBOPF_BREAK>
TAXI_SUBOP_MOVE_BIT           EQU         000000040h
TAXI_SUBOP_MOVE_MASK          EQU         0ffffffbfh
TAXI_SUBOP_BREAK        EQU         0t
TAXI_SUBOP_ILS_HOLD           EQU         1t
TAXI_SUBOP_RUNWAY_HOLD        EQU         2t
TAXI_SUBOP_TAXI_HOLD          EQU         3t
TAXI_SUBOP_SOLID_SOLID_EDGE         EQU         4t
TAXI_SUBOP_DASHED_DASHED_EDGE       EQU         5t
TAXI_SUBOP_DASHED_SOLID_EDGE        EQU         6t
TAXI_SUBOP_CENTER       EQU         7t
TAXI_SUBOP_ARC          EQU         8t
TAXI_SUBOP_SOLID_SOLID_EDGE_LIGHTED       EQU         9t
TAXI_SUBOP_DASHED_DASHED_EDGE_LIGHTED           EQU         10t
TAXI_SUBOP_DASHED_SOLID_EDGE_LIGHTED            EQU         11t
TAXI_SUBOP_CENTER_LIGHTED           EQU         12t
TAXI_SUBOP_ARC_LIGHTED        EQU         13t
TAXI_SUBOPF_BREAK       EQU         128t
TAXI_SUBOPF_ILS_HOLD          EQU         129t
TAXI_SUBOPF_RUNWAY_HOLD       EQU         130t
TAXI_SUBOPF_TAXI_HOLD         EQU         131t
TAXI_SUBOPF_SOLID_SOLID_EDGE        EQU         132t
TAXI_SUBOPF_DASHED_DASHED_EDGE            EQU         133t
TAXI_SUBOPF_DASHED_SOLID_EDGE       EQU         134t
TAXI_SUBOPF_CENTER            EQU         135t
TAXI_SUBOPF_ARC         EQU         136t
TAXI_SUBOPF_SOLID_SOLID_EDGE_LIGHTED            EQU         137t
TAXI_SUBOPF_DASHED_DASHED_EDGE_LIGHTED          EQU         138t
TAXI_SUBOPF_DASHED_SOLID_EDGE_LIGHTED           EQU         139t
TAXI_SUBOPF_CENTER_LIGHTED          EQU         140t
TAXI_SUBOPF_ARC_LIGHTED       EQU         141t
TAXI_SUBOPF_INVISIBLE_SOLID_SOLID_EDGE          EQU         196t
TAXI_SUBOPF_INVISIBLE_DASHED_DASHED_EDGE        EQU         197t
TAXI_SUBOPF_INVISIBLE_DASHED_SOLID_EDGE         EQU         198t
TAXI_SUBOPF_INVISIBLE_CENTER        EQU         199t
 
TAXI_SUBOP        TYPEDEF           SDWORD
 
PTAXI_SUBOP       TYPEDEF           PTR SDWORD
 
PPTAXI_SUBOP            TYPEDEF           PTR PTR SDWORD
 
BGL_LIGHT_TYPE_UNDEFINED            EQU         0t
BGL_LIGHT_TYPE_POINT          EQU         1t
BGL_LIGHT_TYPE_SPOT           EQU         2t
BGL_LIGHT_TYPE_LARGE_HALO           EQU         3t
BGL_LIGHT_TYPE_SMALL_HALO           EQU         4t
 
BGL_LIGHT_TYPE          TYPEDEF           SDWORD
 
PBGL_LIGHT_TYPE         TYPEDEF           PTR SDWORD
 
PPBGL_LIGHT_TYPE        TYPEDEF           PTR PTR SDWORD
 
WEATHER_RIDGE_LIFT            EQU         1t
WEATHER_UNI_TURBULENCE        EQU         2t
WEATHER_DIR_TURBULENCE        EQU         3t
WEATHER_THERMAL         EQU         4t
 
WEATHERTYPE       TYPEDEF           SDWORD
 
PWEATHERTYPE            TYPEDEF           PTR SDWORD
 
PPWEATHERTYPE           TYPEDEF           PTR PTR SDWORD
 
BGLOP_INVALID           EQU         00000ffffh
LIBRARY_TYPE_DYNAMIC          EQU         000000002h
LIBRARY_PROPELLERS            EQU         000000080h
LIBRARY_WEAPONRY        EQU         000000090h
LIBRARY_ALL       EQU         0ffffffffh
LIBRARY_BUILDINGS       EQU         000000100h
LIBRARY_BLD_GENERIC           EQU         000000101h
LIBRARY_BLD_ENGLISH           EQU         000000102h
LIBRARY_BLD_FRENCH            EQU         000000103h
LIBRARY_BLD_GERMAN            EQU         000000104h
LIBRARY_BLD_HOUSES            EQU         000000105h
LIBRARY_BLD_CHURCHES          EQU         000000106h
LIBRARY_BLD_CASTLES           EQU         000000107h
LIBRARY_BLD_FAST_FOOD         EQU         000000108h
LIBRARY_BLD_BARNS       EQU         000000109h
LIBRARY_BLD_STADIUMS          EQU         000000110h
LIBRARY_BLD_INDUSTRIAL        EQU         000000111h
LIBRARY_LANDMARKS       EQU         000000200h
LIBRARY_LND_GENERIC           EQU         000000201h
LIBRARY_LND_BERLIN            EQU         000000202h
LIBRARY_LND_LONDON            EQU         000000203h
LIBRARY_LND_PARIS       EQU         000000204h
LIBRARY_LND_CHICAGO           EQU         000000205h
LIBRARY_LND_NEW_YORK          EQU         000000206h
LIBRARY_LND_BOSTON            EQU         000000207h
LIBRARY_LND_DC          EQU         000000208h
LIBRARY_LND_SEATTLE           EQU         000000209h
LIBRARY_LND_ROME        EQU         000000210h
LIBRARY_LND_LOS_ANGELES       EQU         000000211h
LIBRARY_LND_TOYKO       EQU         000000212h
LIBRARY_LND_SAN_FRANCISCO           EQU         000000213h
LIBRARY_LND_EUROPEAN          EQU         000000214h
LIBRARY_LND_ASIAN       EQU         000000215h
LIBRARY_LND_NORTH_AMERICAN          EQU         000000216h
LIBRARY_LND_OCEANIC           EQU         000000217h
LIBRARY_LND_AFRICAN           EQU         000000218h
LIBRARY_LND_SOUTH_AMERICAN          EQU         000000219h
LIBRARY_VEHICLES        EQU         000000400h
LIBRARY_VEH_TRUCKS            EQU         000000401h
LIBRARY_VEH_CARS        EQU         000000402h
LIBRARY_VEH_HEAVY_EQUIPMENT         EQU         000000403h
LIBRARY_VEH_TRAINS            EQU         000000404h
LIBRARY_VEH_MISC        EQU         000000405h
LIBRARY_VEH_AIRPORT           EQU         000000406h
LIBRARY_SHIPS_TRAINS          EQU         000000800h
LIBRARY_AIRCRAFT        EQU         000001000h
LIBRARY_VEGETATION            EQU         000002000h
LIBRARY_WATER_OBJECTS         EQU         000004000h
LIBRARY_WAT_CRUISE            EQU         000004001h
LIBRARY_WAT_SAILBOATS         EQU         000004002h
LIBRARY_WAT_CARGO       EQU         000004003h
LIBRARY_WAT_MILITARY          EQU         000004004h
LIBRARY_WAT_MISC        EQU         000004005h
LIBRARY_WAT_MOTOR       EQU         000004006h
LIBRARY_AIRPORT_OBJECTS       EQU         000008000h
LIBRARY_AIR_TOWERS            EQU         000008001h
LIBRARY_AIR_HANGERS           EQU         000008002h
LIBRARY_AIR_MISC        EQU         000008003h
LIBRARY_SPECIAL_INTEREST            EQU         000010000h
LIBRARY_SPC_DAMS        EQU         000010001h
LIBRARY_SPC_WORLD_WONDERS           EQU         000010002h
LIBRARY_SPC_MISC        EQU         000010003h
LIBRARY_BRIDGES         EQU         000020000h
LIBRARY_BRG_SUSPENSION        EQU         000020001h
LIBRARY_BRG_TRUSS       EQU         000020002h
LIBRARY_BRG_SPAN        EQU         000020003h
LIBRARY_BRG_DRAW        EQU         000020004h
LINEAR_TILING           EQU         000000000h
MIRROR_TILING           EQU         000000001h
RESERVED_TILING1        EQU         000000002h
RESERVED_TILING2        EQU         000000003h
RESERVED_TILING3        EQU         000000004h
RESERVED_TILING4        EQU         000000005h
RESERVED_TILING5        EQU         000000006h
RESERVED_TILING6        EQU         000000007h
NO_TEXTURE_VARIATIONS         EQU         000000000h
TEXTURE_VARIATIONS            EQU         000000001h
TEXTURE_AIRCRAFT        EQU         1t
TEXTURE_MAP       EQU         2t
TEXTURE_WATER           EQU         3t
TEXTURE_SKY       EQU         4t
TEXTURE_GROUND          EQU         5t
TEXTURE_BUILDING        EQU         6t
TEXTURE_EFFECT          EQU         7t
TEXTURE_DAMAGE          EQU         8t
TEXTURE_NIGHTMAP        EQU         000000080h
TEXTURE_SPRING          TEXTEQU           <(BIT3)>
TEXTURE_FALL            TEXTEQU           <(BIT4)>
TEXTURE_WINTER          TEXTEQU           <(BIT5)>
TEXTURE_HARDWINTER            TEXTEQU           <(BIT6)>
TEXTURE_SEASON          TEXTEQU           <(BIT5 | BIT4 | BIT3)>
TEXTURE2_MASK           EQU         00000ff00h
TEXTURE2_NONE           EQU         00000ff00h
TEXTURE2_NIGHT          EQU         000000100h
TEXTURE2_REFLECT        EQU         000000200h
TEXTURE2_LIGHTMAP       EQU         000000300h
TEXTURE2_LIGHTMAP_A           EQU         000000400h
TEXTURE2_DETAIL         EQU         000000500h
TEXTURE2_SHADER         EQU         000000f00h
CLASS_TEXTURE_WATER           EQU         101t
CLASS_TEXTURE_OCEAN_BANK            EQU         102t
CLASS_TEXTURE_HARBOR_CHANNEL        EQU         103t
CLASS_TEXTURE_REEF            EQU         104t
CLASS_TEXTURE_BLUE_WATER            EQU         105t
CLASS_TEXTURE_BROWN_WATER           EQU         106t
CLASS_TEXTURE_TAN_WATER       EQU         107t
CLASS_TEXTURE_MARSH           EQU         108t
CLASS_TEXTURE_SWAMP           EQU         109t
BGL_TEXT_CENTERED_TEXT        TEXTEQU           <BIT0>
BGL_TEXT_CENTERED_TOP_TEXT          TEXTEQU           <BIT1>
BGL_TEXT_CENTERED_BOTTOM_TEXT       TEXTEQU           <BIT2>
BGL_TEXT_CENTERED_RIGHT_TEXT        TEXTEQU           <BIT3>
BGL_TEXT_CENTERED_LEFT_TEXT         TEXTEQU           <BIT4>
BGL_TEXT_UPPER_RIGHT_TEXT           TEXTEQU           <BIT5>
BGL_TEXT_LOWER_RIGHT_TEXT           TEXTEQU           <BIT6>
BGL_TEXT_UPPER_LEFT_TEXT            TEXTEQU           <BIT7>
BGL_TEXT_LOWER_LEFT_TEXT            TEXTEQU           <BIT8>
BGL_TEXT_DROP_SHADOW_TEXT           TEXTEQU           <BIT9>
BGL_TEXT_FONT_SMALL           TEXTEQU           <BIT10>
BGL_TEXT_FONT_CUSTOM_NORMAL         TEXTEQU           <BIT11>
BGL_TEXT_FONT_CUSTOM_BOLD           TEXTEQU           <(BIT10 | BIT11)>
BGL_TEXT_FONT_FIXED           TEXTEQU           <BIT12>
BGL_TEXT_ALIGN_MASK           TEXTEQU           <(BIT0 | BIT1 | BIT2 | BIT3 | BIT4 | BIT5 | BIT6 | BIT7 | BIT8)>
BGL_TEXT_FONT_MASK            TEXTEQU           <(BIT10 | BIT11 | BIT12)>
BGL_TEXT_VALID_MASK           EQU         000003fffh
ROAD_TEXTURE_NONE       EQU         0t
ROAD_TEXTURE_CURRENT          EQU         1t
ROAD_TEXTURE_STYLE1           EQU         2t
ROAD_TEXTURE_STYLE2           EQU         3t
ROAD_TEXTURE_RAILROAD         EQU         4t
ROAD_TEXTURE_RIVER            EQU         5t
VAR_BASE_PARAMS         EQU         -1t
VAR_BASE_GLOBAL         EQU         0t
VAR_BASE_LOCAL          EQU         1t
CAT_SHIPS         EQU         2t
CAT_MESH          EQU         4t
CAT_POLY          EQU         8t
CAT_RIVER         EQU         12t
CAT_ROAD          EQU         16t
CAT_LINE          EQU         20t
CAT_RUNWAY        EQU         24t
CAT_MOUNTAIN            EQU         28t
CAT_CRATER        EQU         32t
CAT_GROUND_ELEMENT            EQU         40t
CAT_SHADOWS       EQU         60t
OBJECTOP_BUILDING_RECT_FLAT_ROOF          EQU         1t
OBJECTOP_BUILDING_RECT_RIDGE_ROOF         EQU         2t
OBJECTOP_BUILDING_RECT_PEAK_ROOF          EQU         3t
OBJECTOP_BUILD_RECT_FLAT_ROOF       EQU         4t
OBJECTOP_BUILD_RECT_RIDGE_ROOF            EQU         6t
OBJECTOP_BUILD_RECT_PEAK_ROOF       EQU         7t
OBJECTOP_BUILD_RECT_SLANT_ROOF            EQU         8t
OBJECTOP_BUILD_PYRAMID        EQU         9t
OBJECTOP_BUILD_N_SIDED        EQU         10t
OBJECTOP_BUILD_OCTAGANAL            EQU         11t
OBJECTOP_BEACON_CIVILIAN_AIRPORT          EQU         501t
OBJECTOP_BEACON_CIVILIAN_HELIPORT         EQU         502t
OBJECTOP_BEACON_CIVILIAN_WATER            EQU         503t
OBJECTOP_BEACON_MILITARY_AIRPORT          EQU         504t
OBJECTOP_BEACON_MILITARY_HELIPORT         EQU         505t
OBJECTOP_BEACON_MILITARY_WATER            EQU         506t
OBJECTOP_WINDSOCK       EQU         521t
OBJECTOP_CRASH          EQU         600t
OBJECTOP_EFFECT         EQU         620t
BUILDING_WALL_TEXTURE_MAX           EQU         122t
BUILDING_WALL_TEXTURE_OLD           EQU         86t
BUILDING_ROOF_TEXTURE_MAX           EQU         38t
BUILDING_ROOF_TEXTURE_OLD           EQU         34t
BUILDING_WINDOW_TEXTURE_MAX         EQU         103t
BUILDING_WINDOW_TEXTURE_OLD         EQU         85t
RUNWAY_SURFACE_DIRT           EQU                   0o
RUNWAY_SURFACE_CEMENT         EQU         1t
RUNWAY_SURFACE_ASPHALT        EQU         2t
RUNWAY_SURFACE_GRASS          EQU         3t
RUNWAY_SURFACE_CORAL          EQU         4t
RUNWAY_SURFACE_GRAVEL         EQU         5t
RUNWAY_SURFACE_OIL_TREATED          EQU         6t
RUNWAY_SURFACE_STEEL_MATS           EQU         7t
RUNWAY_SURFACE_SNOW           EQU         8t
RUNWAY_SURFACE_BITUMINUS            EQU         11t
RUNWAY_SURFACE_BRICK          EQU         12t
RUNWAY_SURFACE_CLAY           EQU         13t
RUNWAY_SURFACE_MACADAM        EQU         14t
RUNWAY_SURFACE_PLANKS         EQU         15t
RUNWAY_SURFACE_SAND           EQU         16t
RUNWAY_SURFACE_SHALE          EQU         17t
RUNWAY_SURFACE_TARMAC         EQU         18t
RUNWAY_SURFACE_ICE            EQU         19t
RUNWAY_SURFACE_DIRT_FUZZY           EQU         64t
RUNWAY_SURFACE_DIRT_ROUND           EQU         65t
RUNWAY_SURFACE_STEEL_MATS_CFS       EQU         66t
RUNWAY_SURFACE_CORAL_FUZZY          EQU         67t
RUNWAY_SURFACE_CORAL_ROUND          EQU         68t
C_BLACK           EQU         00000f000h
C_DKGRAY          EQU         00000f001h
C_GRAY            EQU         00000f002h
C_LTGRAY          EQU         00000f003h
C_WHITE           EQU         00000f004h
C_RED       EQU         00000f005h
C_GREEN           EQU         00000f006h
C_BLUE            EQU         00000f007h
C_ORANGE          EQU         00000f008h
C_YELLOW          EQU         00000f009h
C_BROWN           EQU         00000f00ah
C_TAN       EQU         00000f00bh
C_BRICK           EQU         00000f00ch
C_OLIVE           EQU         00000f00dh
C_WATER           EQU         00000f00eh
C_BRIGHT_RED            EQU         00000f00fh
C_BRIGHT_GREEN          EQU         00000f010h
C_BRIGHT_BLUE           EQU         00000f011h
C_BRIGHT_AQUA           EQU         00000f012h
C_BRIGHT_ORANGE         EQU         00000f013h
C_BRIGHT_YELLOW         EQU         00000f014h
C_BRIGHT_WHITE          EQU         00000f015h
C_CONST_WHITE           EQU         00000f016h
C_DARK_RED        EQU         00000f017h
C_DARK_GREEN            EQU         00000f018h
C_DARK_BLUE       EQU         00000f019h
C_DARK_ORANGE           EQU         00000f01ah
C_DARK_YELLOW           EQU         00000f01bh
C_DARK_BROWN            EQU         00000f01ch
C_DARK_TAN        EQU         00000f01dh
C_DARK_BRICK            EQU         00000f01eh
C_DARK_OLIVE            EQU         00000f01fh
C_MED_RED         EQU         00000f020h
C_MED_GREEN       EQU         00000f021h
C_MED_BLUE        EQU         00000f022h
C_MED_ORANGE            EQU         00000f023h
C_MED_YELLOW            EQU         00000f024h
C_MED_BROWN       EQU         00000f025h
C_MED_TAN         EQU         00000f026h
C_MED_BRICK       EQU         00000f027h
C_MED_OLIVE       EQU         00000f028h
C_LIGHT_RED       EQU         00000f029h
C_LIGHT_GREEN           EQU         00000f02ah
C_LIGHT_BLUE            EQU         00000f02bh
C_LIGHT_ORANGE          EQU         00000f02ch
C_LIGHT_YELLOW          EQU         00000f02dh
C_LIGHT_BROWN           EQU         00000f02eh
C_LIGHT_TAN       EQU         00000f02fh
C_LIGHT_BRICK           EQU         00000f030h
C_LIGHT_OLIVE           EQU         00000f031h
C_BRIGHT_DKGRAY         EQU         00000f032h
C_BRIGHT_GRAY           EQU         00000f033h
C_BRIGHT_LTGRAY         EQU         00000f034h
G_DKGRAY          EQU         00000f001h
G_GRAY            EQU         00000f002h
G_LTGRAY          EQU         00000f003h
G_WHITE           EQU         00000f004h
G_RED       EQU         00000f005h
G_GREEN           EQU         00000f006h
G_BLUE            EQU         00000f007h
G_ORANGE          EQU         00000f008h
G_YELLOW          EQU         00000f009h
G_BROWN           EQU         00000f00ah
G_TAN       EQU         00000f00bh
G_BRICK           EQU         00000f00ch
G_OLIVE           EQU         00000f00dh
C_FS5_VAL         EQU         00000f000h
C_RGB_VAL         EQU         00000e000h
C_BRIGHT_RGB_VAL        EQU         00000b000h
MOUSERECT_TOOLTIP       EQU         1t
MOUSERECT_PARMS         EQU         2t
MOUSERECT_FUNCTION_LANGUAGE         EQU         1t
MOUSERECT_FUNCTION_DRAG       EQU         2t
MOUSERECT_FUNCTION_DRAG_STEPS       EQU         3t
MOUSERECT_MAX_FUNCTION        EQU         3t
BGL_SCENERY_OBJECT_UNKNOWN          EQU         0t
BGL_SCENERY_OBJECT_GENERIC_BUILDING       EQU         1t
BGL_SCENERY_OBJECT_LIBRARY_OBJECT         EQU         2t
BGL_SCENERY_OBJECT_WINDSOCK         EQU         3t
BGL_SCENERY_OBJECT_EFFECT           EQU         4t
BGL_SCENERY_OBJECT_TAXIWAY_SIGNS          EQU         5t
BGL_SCENERY_OBJECT_MODEL_DATA       EQU         6t
BGL_SCENERY_OBJECT_TRIGGER          EQU         7t
BGL_SCENERY_OBJECT_BEACON           EQU         8t
BGL_SCENERY_OBJECT_PROXY_OBJECT           EQU         9t
BGL_SCENERY_OBJECT_ATTACHED_OBJECT_START        EQU         4096t
BGL_SCENERY_OBJECT_ATTACHED_OBJECT_END          EQU         4097t
BGL_SCENERY_OBJECT_MAC        EQU         4098t
 
BGL_SCENERY_OBJECT_TYPE       TYPEDEF           SDWORD
 
PBGL_SCENERY_OBJECT_TYPE            TYPEDEF           PTR SDWORD
 
PPBGL_SCENERY_OBJECT_TYPE           TYPEDEF           PTR PTR SDWORD
 
BGL_ATTACH_POINT_MAX_NAME_LENGTH          EQU         128t
BGL_PLATFORM_MAX_NAME_LENGTH        EQU         128t
BGL_PLATFORM_MAX_VERTEX_COUNT       EQU         255t
TAXIWAY_SIGN_JUSTIFICATION_UNKNOWN        EQU         0t
TAXIWAY_SIGN_JUSTIFICATION_LEFT           EQU         1t
TAXIWAY_SIGN_JUSTIFICATION_RIGHT          EQU         2t
 
TAXIWAY_SIGN_JUSTIFICATION          TYPEDEF           SDWORD
 
PTAXIWAY_SIGN_JUSTIFICATION         TYPEDEF           PTR SDWORD
 
PPTAXIWAY_SIGN_JUSTIFICATION        TYPEDEF           PTR PTR SDWORD
 
TAXIWAY_SIGN_SIZE_UNKNOWN           EQU         0t
TAXIWAY_SIGN_SIZE_1           EQU         1t
TAXIWAY_SIGN_SIZE_2           EQU         2t
TAXIWAY_SIGN_SIZE_3           EQU         3t
TAXIWAY_SIGN_SIZE_4           EQU         4t
TAXIWAY_SIGN_SIZE_5           EQU         5t
 
TAXIWAY_SIGN_SIZE       TYPEDEF           SDWORD
 
PTAXIWAY_SIGN_SIZE            TYPEDEF           PTR SDWORD
 
PPTAXIWAY_SIGN_SIZE           TYPEDEF           PTR PTR SDWORD
 
DAYLIGHT_SAVINGS_NONE         EQU         0t
DAYLIGHT_SAVINGS_US           EQU         1t
DAYLIGHT_SAVINGS_CANADA       EQU         2t
DAYLIGHT_SAVINGS_BRITIAN            EQU         3t
DAYLIGHT_SAVINGS_CENTRAL_EUROPE           EQU         4t
DAYLIGHT_SAVINGS_EASTERN_EUROPE           EQU         5t
DAYLIGHT_SAVINGS_MAX          EQU         6t
 
DAYLIGHT_SAVINGS_TYPE         TYPEDEF           SDWORD
 
PDAYLIGHT_SAVINGS_TYPE        TYPEDEF           PTR SDWORD
 
 
;-----------------------------------------------------------------------------
;     NOTE: MACROS CAN HAVE A MAXIMUM OF 25 ARGUMENTS
;-----------------------------------------------------------------------------
 
 
BGL   macro
      dw    76h
      endm
 
BGL_EVEN    macro
      db    76h
      EVEN
      endm
 
EOF   macro
      dw    00h
      endm
 
LOGOL macro
      dw    01h
      endm
 
NOOP  macro
      dw    02h
      endm
 
 
DEBUG macro
      dw    04h
      endm
 
 
SURFACE     macro
      dw    05h
      endm
 
 
SPNT  macro xx,yy,zz
      dw    06h
      dw    xx
      dw    yy
      dw    zz
      endm
 
 
CPNT  macro xx,yy,zz
      dw    07h
      dw    xx
      dw    yy
      dw    zz
      endm
 
 
CLOSURE     macro
      dw    08h
      endm
 
 
GSURF macro
      dw    09h
      endm
 
 
GSPNT macro ii,xx,yy,zz
      dw    0ah
      dw    ii
      dw    xx
      dw    yy
      dw    zz
      endm
 
 
GCPNT macro ii,xx,yy,zz
      dw    0bh
      dw    ii
      dw    xx
      dw    yy
      dw    zz
      endm
 
 
GCLOSURE    macro
      dw    0ch
      endm
 
;
; ERRS16  generate a error if the passed offset
; cant fit in a signed 16bit WORD
;
ERRS16      macro x
      .errnz      (((x) + 32768) AND 0FFFF0000h)
      endm
 
;
; ERRS8  generate a error if the passed offset
; cant fit in a signed 8bit BYTE
;
ERRS8 macro x
      .errnz      (((x) + 128) AND 0FFFFFF00h)
      endm
 
 
JUMP  macro dest
      local start
start label word
      dw    0dh
      dw    (offset dest)-(offset start)
      ERRS16      (offset dest)-(offset start)
      endm
 
 
BGL_JUMP_32 macro routine
      local start
start label word
      dw    088h
      dd    (offset routine)-(offset start)
      endm
 
 
SETCOLOR    macro color
      dw    14h
      dw    color
      endm
 
 
GDEFRES     macro n,i,x,y,z
      dw    11h,n,i,x,y,z
      endm
 
 
GSTRRES     macro n
      dw    12h,n
      endm
 
 
GCNTRES     macro n
      dw    13h,n
      endm
 
 
DEFRES      macro n,x,y,z
      dw    0eh,n,x,y,z
      endm
 
 
STRRES      macro n
      dw    0fh,n
      endm
 
 
CNTRES      macro n
      dw    10h,n
      endm
 
 
TEXTURE macro   n,ix,iy,iz,name
      local name_start, name_end
      dw    18h
      if    n eq 1
            dw    0C000h
      else
            if    n eq 2
                  dw    08000h
            else
                  if    n eq 3
                        dw    04000h
                  else
                        dw    0
                  endif
            endif
      endif
      dw    ix,iy,iz
name_start label byte
      db    name,0,0
name_end label byte
if    ((offset name_end) - (offset name_start)) le 13
      %out  texture name is too short!
      rept 14 - ((offset name_end) - (offset name_start))
            db 0
      endm
      rept 14 - ((offset name_end) - (offset name_start))
            db 0
      endm
      .err        ; comment this line out to 'save the users butt'
endif
if    ((offset name_end) - (offset name_start)) ge 15
      %out  texture name is too long!
      .err
endif
      endm
 
 
TEXTURE_REPEAT    macro ix,iy,iz
      dw    05Dh
      dw    ix,iy,iz
      endm
 
 
TEXTURE_ROTATE    macro pitch,bank,heading
      dw    05Eh
      dw    [(pitch/90)*256] + [(bank/90)*16] + [heading/90]
      endm
 
 
TEXTURE_ENABLE    macro parm
      dw    017h,parm
      endm
 
 
PALETTE     macro name
      dw    19h
      db    name,0,0
      endm
 
;;
;; BGL_COLOR    - omit a UNICOL
;;
;;    BGL_COLOR   x               UNICOL
;;    BGL_COLOR   r,g,b     24 bit color
;;    BGL_COLOR   r,g,b,a         32 bit color with alpha
;;    BGL_COLOR   r,g,b,BRIGHT    bright 24 bit color
;;    BGL_COLOR   r,g,b,a,BRIGHT  bright 32 bit color with alpha
;;
;;    24 bit RGBA color are packed into a UNICOL32 like so
;;    the second byte is the magic byte that flags this color
;;    as a full RGB not a FS5 color.
;;
;;    bbggEarr    - RGBA UNICOL
;;    bbggBarr    - RGBA UNICOL (bright)
;;
BRIGHT            = 0FFFFh    ; special flag to use with this macro only
C_RGB       = 0E0h            ; magic value in UNICOL for 24bit RGB
C_BRIGHT_RGB      = 0B0h            ; magic value in UNICOL for 24bit bright RGB
 
BGL_COLOR macro r,g,b,a,f
ifnb <b>                      ; r,g,b case
    db      r                       ; output red
    ifnb <f>                        ; r,g,b,a,f case
      if f eq BRIGHT                ; r,g,b,a,BRIGHT case
          db      C_BRIGHT_RGB + (a / 16) ; output bright RGB flag + alpha
      else
          db      C_RGB + (a / 16)  ; output RGB flag + alpha
      endif
    else
      ifnb <a>                ; r,g,b,a case
          if a eq BRIGHT            ; r,g,b,BRIGHT case
            db  C_BRIGHT_RGB + 0Fh  ; output bright RGB flag + alpha=255
          else                ; r,g,b,a case
            db  C_RGB + (a / 16)    ; output RGB flag + alpha
          endif
      else                    ; r,g,b case
          db      C_RGB + 0Fh       ; output RGB flag + alpha=255
      endif
    endif
    db      g                       ; output green
    db      b                       ; output blue
else                          ; x case
    dd      r                       ; output UNICOL
endif
    endm
 
BGL_TEXTURE macro tclass,color,name
      local texture_start,texture_end0,texture_end
texture_start     label word
      dw    043h
      dw    (offset texture_end-texture_start)
      dw    0                             ; priority/index
      dw    tclass
      BGL_COLOR color   ;; dd      color
ifnb <name>
      db    name,0
else
      db    -1, 0     ; no name specified, disable texturing
endif
texture_end0      label word
      IF    (offset texture_end0 - offset texture_start) AND 1
      db    0
      ENDIF
texture_end label word
      ERRS16      (offset texture_end - offset texture_start)
      endm
 
BGL_LIST    macro name,count
name  label word
      dw    064h
      dw    (offset &name&_end_list - offset name)
      dw    count
      dw    count dup(0);
      ERRS16      (offset &name&_end_list - offset name)
      endm
 
BGL_LIST_END      macro name
&name&_end_list label word
      endm
 
BGL_SELECT  macro var,vmask,tlist
      local start
start label word
      dw    07Ch
      dw    var
      dw    vmask
      dd    (offset tlist - offset start)
      endm
 
 
RESLIST     macro start,number
      dw    1ah
      dw    start,number
      endm
 
 
VRESLIST    macro list_ofs,start,number
      dw    09Bh
      dw    list_ofs,start,number
      endm
 
 
VERTEX      macro x,y,z
      dw    x,y,z
      endm
 
RESROW      macro start,number,xs,ys,zs,xe,ye,ze
      dw    031h
      dw    start,number
      dw    xs,ys,zs
      dw    xe,ye,ze
      endm
 
FACE3 macro px,py,pz,nx,ny,nz,p1,p2,p3
      dw    1dh,3
      dw    px,py,pz,nx,ny,nz
      dw    p1,p2,p3
      endm
 
 
FACE4 macro px,py,pz,nx,ny,nz,p1,p2,p3,p4
      dw    1dh,4
      dw    px,py,pz,nx,ny,nz
      dw    p1,p2,p3,p4
      endm
 
 
FACE5 macro px,py,pz,nx,ny,nz,p1,p2,p3,p4,p5
      dw    1dh,5
      dw    px,py,pz,nx,ny,nz
      dw    p1,p2,p3,p4,p5
      endm
 
 
FACE6 macro px,py,pz,nx,ny,nz,p1,p2,p3,p4,p5,p6
      dw    1dh,6
      dw    px,py,pz,nx,ny,nz
      dw    p1,p2,p3,p4,p5,p6
      endm
 
FACE7 macro px,py,pz,nx,ny,nz,p1,p2,p3,p4,p5,p6,p7
      dw    1dh,7
      dw    px,py,pz,nx,ny,nz
      dw    p1,p2,p3,p4,p5,p6,p7
      endm
 
FACE8 macro px,py,pz,nx,ny,nz,p1,p2,p3,p4,p5,p6,p7,p8
      dw    1dh,8
      dw    px,py,pz,nx,ny,nz
      dw    p1,p2,p3,p4,p5,p6,p7,p8
      endm
 
FACE  macro      px,py,pz,nx,ny,nz,p1,p2,p3,p4,p5,p6,p7,p8,p9,p10,p11,p12,p13,p14,p15,p16,p17,p18,p19,p20,p21,p22,p23,p24,p25,p26,p27,p28,p29,p30,p31,p32
      local lb1,lb2
      dw    01Dh
      dw    [(lb2-lb1)/2]
      dw    px,py,pz,nx,ny,nz
lb1   dw    p1,p2,p3
      ifnb  <p4>
      dw    p4
      endif
      ifnb  <p5>
      dw    p5
      endif
      ifnb  <p6>
      dw    p6
      endif
      ifnb  <p7>
      dw    p7
      endif
      ifnb  <p8>
      dw    p8
      endif
      ifnb  <p9>
      dw    p9
      endif
      ifnb  <p10>
      dw    p10
      endif
      ifnb  <p11>
      dw    p11
      endif
      ifnb  <p12>
      dw    p12
      endif
      ifnb  <p13>
      dw    p13
      endif
      ifnb  <p14>
      dw    p14
      endif
      ifnb  <p15>
      dw    p15
      endif
      ifnb  <p16>
      dw    p16
      endif
      ifnb  <p17>
      dw    p17
      endif
      ifnb  <p18>
      dw    p18
      endif
      ifnb  <p19>
      dw    p19
      endif
      ifnb  <p20>
      dw    p20
      endif
      ifnb  <p21>
      dw    p21
      endif
      ifnb  <p22>
      dw    p22
      endif
      ifnb  <p23>
      dw    p23
      endif
      ifnb  <p24>
      dw    p24
      endif
      ifnb  <p25>
      dw    p25
      endif
      ifnb  <p26>
      dw    p26
      endif
      ifnb  <p27>
      dw    p27
      endif
      ifnb  <p28>
      dw    p28
      endif
      ifnb  <p29>
      dw    p29
      endif
      ifnb  <p30>
      dw    p30
      endif
      ifnb  <p31>
      dw    p31
      endif
      ifnb  <p32>
      dw    p32
      endif
lb2   label word
      endm
 
 
 
BGL_DEBUG   macro
__debug_    = $
      dw    04h
      NOOP
      endm
 
 
BGL_DEBUG_END     macro
      retf
      EVEN
__debug_end_      = $
      org   __debug_
      dw    016h
      dw    (__debug_end_ -__debug_)
      org   __debug_end_
      endm
 
 
HAZE  macro val
      dw    1eh,val
      endm
 
HORIZON     macro val
      dw    1fh,val
      endm
 
FACET3_TMAP macro a,b,c,d,p1,t1x,t1z,p2,t2x,t2z,p3,t3x,t3z
      dw    20h,3
      dw    a,b,c
      dd    d
      dw    p1,t1x,t1z
      dw    p2,t2x,t2z
      dw    p3,t3x,t3z
      endm
 
FACET4_TMAP macro a,b,c,d,p1,t1x,t1z,p2,t2x,t2z,p3,t3x,t3z,p4,t4x,t4z
      dw    20h,4
      dw    a,b,c
      dd    d
      dw    p1,t1x,t1z
      dw    p2,t2x,t2z
      dw    p3,t3x,t3z
      dw    p4,t4x,t4z
      endm
 
FACET5_TMAP macro a,b,c,d,p1,t1x,t1z,p2,t2x,t2z,p3,t3x,t3z,p4,t4x,t4z,p5,t5x,t5z
      dw    20h,5
      dw    a,b,c
      dd    d
      dw    p1,t1x,t1z
      dw    p2,t2x,t2z
      dw    p3,t3x,t3z
      dw    p4,t4x,t4z
      dw    p5,t5x,t5z
      endm
 
FACET6_TMAP macro a,b,c,d,p1,t1x,t1z,p2,t2x,t2z,p3,t3x,t3z,p4,t4x,t4z,p5,t5x,t5z,p6,t6x,t6z
      dw    20h,6
      dw    a,b,c
      dd    d
      dw    p1,t1x,t1z
      dw    p2,t2x,t2z
      dw    p3,t3x,t3z
      dw    p4,t4x,t4z
      dw    p5,t5x,t5z
      dw    p6,t6x,t6z
      endm
 
FACET7_TMAP macro      a,b,c,d,p1,t1x,t1z,p2,t2x,t2z,p3,t3x,t3z,p4,t4x,t4z,p5,t5x,t5z,p6,t6x,t6z,p7,t7x,t7z
      dw    20h,7
      dw    a,b,c
      dd    d
      dw    p1,t1x,t1z
      dw    p2,t2x,t2z
      dw    p3,t3x,t3z
      dw    p4,t4x,t4z
      dw    p5,t5x,t5z
      dw    p6,t6x,t6z
      dw    p7,t7x,t7z
      endm
 
FACET8_TMAP macro      a,b,c,d,p1,t1x,t1z,p2,t2x,t2z,p3,t3x,t3z,p4,t4x,t4z,p5,t5x,t5z,p6,t6x,t6z,p7,t7x,t7z,p8,t8x,t8z
      dw    20h,8
      dw    a,b,c
      dd    d
      dw    p1,t1x,t1z
      dw    p2,t2x,t2z
      dw    p3,t3x,t3z
      dw    p4,t4x,t4z
      dw    p5,t5x,t5z
      dw    p6,t6x,t6z
      dw    p7,t7x,t7z
      dw    p8,t8x,t8z
      endm
 
FACET9_TMAP macro      a,b,c,d,p1,t1x,t1z,p2,t2x,t2z,p3,t3x,t3z,p4,t4x,t4z,p5,t5x,t5z,p6,t6x,t6z,p7,t7x,t7z,p8,t8x,t8z,p9,t9x,t9z
      dw    20h,9
      dw    a,b,c
      dd    d
      dw    p1,t1x,t1z
      dw    p2,t2x,t2z
      dw    p3,t3x,t3z
      dw    p4,t4x,t4z
      dw    p5,t5x,t5z
      dw    p6,t6x,t6z
      dw    p7,t7x,t7z
      dw    p8,t8x,t8z
      dw    p9,t9x,t9z
      endm
 
SUPERMESH   macro x_grid,z_grid,x_patch,z_patch,x_disp,z_disp,x_view,z_view
      local start
      dw    21h,x_grid,z_grid,x_patch,z_patch,x_disp,z_disp,x_view,z_view
start  label word
supermeshloc      = offset start
      endm
 
SMROUTINE   macro dest
      dw    (offset dest)-(supermeshloc)
      ERRS16      (offset dest)-(supermeshloc)
      endm
 
BGL_CALL    macro routine
      local start
start  label word
      dw    23h
      dw    (offset routine)-(offset start)
      ERRS16      (offset routine)-(offset start)
      endm
 
BGL_CALL_32 macro routine
      local start
start  label word
      dw    08Ah
      dd    (offset routine)-(offset start)
      endm
 
BGL_FAR_CALL      macro routine,segment
      dw    05Ch
      dw    routine
      dw    segment
      endm
 
 
BGL_LIBRARY_CALL  macro id1,id2,id3,id4         ; calls a BGL library
      dw    063h                    ; opcode
      dw    0                       ; quick index lookup
      GUID128     <id1,id2,id3,id4>       ; guid128 values
      endm
 
 
BGL_VLIBRARY_CALL macro var,index ; calls a BGL library
      dw    09Ch              ; opcode
ifnb <index>
      dw    index             ; quick index lookup
else
      dw    0                 ; quick index lookup
endif
      dw    var               ; library id
      endm
 
 
BGL_RETURN  macro
      dw    22h
      endm
 
IFIN1 macro dest,v,low,high
      local start
start  label word
      dw    24h
      dw    (offset dest)-(offset start)
      dw    v,low,high
      ERRS16      (offset dest)-(offset start)
      endm
 
 
IFNOTIN1    macro dest,v,low,high
      local skip
      IFIN1 skip,v,low,high
      BGL_JUMP_32 dest
skip label word
      endm
 
 
IFIN2 macro dest,v1,low1,high1,v2,low2,high2
      local start
start  label word
      dw    1Ch
      dw    (offset dest)-(offset start)
      dw    v1,low1,high1
      dw    v2,low2,high2
      ERRS16      (offset dest)-(offset start)
      endm
 
 
IFIN3 macro dest,v1,low1,high1,v2,low2,high2,v3,low3,high3
      local start
start  label word
      dw    21h
      dw    (offset dest)-(offset start)
      dw    v1,low1,high1
      dw    v2,low2,high2
      dw    v3,low3,high3
      ERRS16      (offset dest)-(offset start)
      endm
 
 
IFINBOXP    macro dest,lowx,highx,lowy,highy,lowz,highz
      local start
start  label word
      dw    73h
      dw    (offset dest)-(offset start)
      dw    lowx,highx
      dw    lowy,highy
      dw    lowz,highz
      ERRS16      (offset dest)-(offset start)
      endm
 
 
IFIN_BOX_PLANE    macro dest,centerdx,centerdy,centerdz,sizex,sizey,sizez,pitch,bank,heading
      local start
start  label word
      dw    1Bh
      dw    (offset dest)-(offset start)
      dw    centerdx,centerdy,centerdz          ; box center offset from the scale command
      dw    sizex,sizey,sizez             ; rotated size of the box
      dw    pitch,bank,heading                  ; box rotation
      ERRS16      (offset dest)-(offset start)
      endm
 
 
 
IFIN_INSTANCED_BOX_PLANE      macro      dest,centerdx,centerdy,centerdz,sizex,sizey,sizez,pitch,bank,heading
      local start
start  label word
      dw    0A9h
      dw    (offset dest)-(offset start)
      dw    centerdx,centerdy,centerdz          ; box center offset from the scale command
      dw    sizex,sizey,sizez             ; rotated size of the box
      dw    pitch,bank,heading                  ; box rotation
      ERRS16      (offset dest)-(offset start)
      endm
 
 
 
SEPARATION_PLANE  macro dest,a,b,c,d
      local start
start  label word
      dw    25h
      dw    (offset dest)-(offset start)
      dw    a,b,c
      dd    d
      ERRS16      (offset dest)-(offset start)
      endm
 
SIDE  macro xv,low,high,r1,r2
      local jump1
      IFIN1 xv,low,high,jump1
      BGL_CALL r1
      BGL_CALL r2
      BGL_RETURN
jump1  label word
      BGL_CALL r2
      BGL_CALL r1
      BGL_RETURN
      endm
 
IFSIDE      macro a,b,c,d,r1,r2
      local jump1
      SEPARATION_PLANE jump1,a,b,c,d
      BGL_CALL r1
      BGL_CALL r2
      BGL_RETURN
jump1  label word
      BGL_CALL r2
      BGL_CALL r1
      BGL_RETURN
      endm
 
IFSIDE_32   macro a,b,c,d,r1,r2
      local jump1
      SEPARATION_PLANE jump1,a,b,c,d
      BGL_CALL_32 r1
      BGL_CALL_32 r2
      BGL_RETURN
jump1  label word
      BGL_CALL_32 r2
      BGL_CALL_32 r1
      BGL_RETURN
      endm
 
IFSIDE_32_3 macro a,b,c,d,r1,r2,r3
      local jump1
      SEPARATION_PLANE jump1,a,b,c,d
      BGL_CALL_32 r1
      BGL_CALL_32 r2
      BGL_CALL_32 r3
      BGL_RETURN
jump1  label word
      BGL_CALL_32 r3
      BGL_CALL_32 r2
      BGL_CALL_32 r1
      BGL_RETURN
      endm
 
IFSIDE_32_NO_RET macro  a,b,c,d,r1,r2
      local jump1
      local jump2
      SEPARATION_PLANE jump1,a,b,c,d
      BGL_CALL_32 r1
      BGL_CALL_32 r2
      JUMP  jump2
jump1  label word
      BGL_CALL_32 r2
      BGL_CALL_32 r1
jump2  label word
      endm
 
IFSIDE_32_3_NO_RET macro a,b,c,d,r1,r2,r3
      local jump1
      local jump2
      SEPARATION_PLANE jump1,a,b,c,d
      BGL_CALL_32 r1
      BGL_CALL_32 r2
      BGL_CALL_32 r3
      JUMP  jump2
jump1  label word
      BGL_CALL_32 r3
      BGL_CALL_32 r2
      BGL_CALL_32 r1
jump2  label word
      endm
 
SETWRD      macro v,n
      dw    26h,v,n
      endm
 
BGL_TEXTURED_FACET3     macro a,b,c,d,p1,p2,p3
      dw    27h,3
      dw    a,b,c
      dd    d
      dw    p1,p2,p3
      endm
 
BGL_TEXTURED_FACET4     macro a,b,c,d,p1,p2,p3,p4
      dw    27h,4
      dw    a,b,c
      dd    d
      dw    p1,p2,p3,p4
      endm
 
 
GRESLIST    macro start,number
      dw    29h
      dw    start,number
      endm
 
GVERTEX     macro x,y,z,nx,ny,nz
      dw    x,y,z,nx,ny,nz
      endm
 
GFACET3     macro a,b,c,d,p1,p2,p3
      dw    2ah,3
      dw    a,b,c
      dd    d
      dw    p1,p2,p3
      endm
 
GFACET4     macro a,b,c,d,p1,p2,p3,p4
      dw    2ah,4
      dw    a,b,c
      dd    d
      dw    p1,p2,p3,p4
      endm
 
GFACET5     macro a,b,c,d,p1,p2,p3,p4,p5
      dw    2ah,5
      dw    a,b,c
      dd    d
      dw    p1,p2,p3,p4,p5
      endm
 
GFACET6     macro a,b,c,d,p1,p2,p3,p4,p5,p6
      dw    2ah,6
      dw    a,b,c
      dd    d
      dw    p1,p2,p3,p4,p5,p6
      endm
 
GFACET7     macro a,b,c,d,p1,p2,p3,p4,p5,p6,p7
      dw    2ah,7
      dw    a,b,c
      dd    d
      dw    p1,p2,p3,p4,p5,p6,p7
      endm
 
GFACET8     macro a,b,c,d,p1,p2,p3,p4,p5,p6,p7,p8
      dw    2ah,8
      dw    a,b,c
      dd    d
      dw    p1,p2,p3,p4,p5,p6,p7,p8
      endm
 
GFACET9     macro a,b,c,d,p1,p2,p3,p4,p5,p6,p7,p8,p9
      dw    2ah,9
      dw    a,b,c
      dd    d
      dw    p1,p2,p3,p4,p5,p6,p7,p8,p9
      endm
 
GFACET10        macro   a,b,c,d,p1,p2,p3,p4,p5,p6,p7,p8,p9,p10
      dw    2ah,0ah
      dw    a,b,c
      dd    d
      dw    p1,p2,p3,p4,p5,p6,p7,p8,p9,p10
      endm
 
GFACET      macro      a,b,c,d,p1,p2,p3,p4,p5,p6,p7,p8,p9,p10,p11,p12,p13,p14,p15,p16,p17,p18,p19,p20,p21,p22,p23,p24,p25,p26,p27,p28,p29,p30,p31,p32
      local lb1,lb2
      dw    02Ah
      dw    [(lb2-lb1)/2]
      dw    a,b,c
      dd    d
lb1   dw    p1,p2,p3
      ifnb  <p4>
      dw    p4
      endif
      ifnb  <p5>
      dw    p5
      endif
      ifnb  <p6>
      dw    p6
      endif
      ifnb  <p7>
      dw    p7
      endif
      ifnb  <p8>
      dw    p8
      endif
      ifnb  <p9>
      dw    p9
      endif
      ifnb  <p10>
      dw    p10
      endif
      ifnb  <p11>
      dw    p11
      endif
      ifnb  <p12>
      dw    p12
      endif
      ifnb  <p13>
      dw    p13
      endif
      ifnb  <p14>
      dw    p14
      endif
      ifnb  <p15>
      dw    p15
      endif
      ifnb  <p16>
      dw    p16
      endif
      ifnb  <p17>
      dw    p17
      endif
      ifnb  <p18>
      dw    p18
      endif
      ifnb  <p19>
      dw    p19
      endif
      ifnb  <p20>
      dw    p20
      endif
      ifnb  <p21>
      dw    p21
      endif
      ifnb  <p22>
      dw    p22
      endif
      ifnb  <p23>
      dw    p23
      endif
      ifnb  <p24>
      dw    p24
      endif
      ifnb  <p25>
      dw    p25
      endif
      ifnb  <p26>
      dw    p26
      endif
      ifnb  <p27>
      dw    p27
      endif
      ifnb  <p28>
      dw    p28
      endif
      ifnb  <p29>
      dw    p29
      endif
      ifnb  <p30>
      dw    p30
      endif
      ifnb  <p31>
      dw    p31
      endif
      ifnb  <p32>
      dw    p32
      endif
lb2   label word
      endm
 
 
 
REJECT      macro dest,x,y,z,radius
      local start
start  label word
      dw    2ch
      dw    (offset dest)-(offset start)
      dw    x,y,z,radius
      ERRS16      (offset dest)-(offset start)
      endm
 
SCOLOR24    macro r,g,b,a,f
      dw    2dh
      BGL_COLOR   r,g,b,a,f
      endm
 
LCOLOR24    macro r,g,b,a,f
      dw    2eh
      BGL_COLOR   r,g,b,a,f
      endm
 
SET_BRIGHTNESS    macro value
      dw    030h
      dw    value
      endm
 
LIBRARY_OBJECT_PTR      macro lib_ptr,guid1,guid2,guid3,guid4
      dd    (lib_ptr - rel_base)    ; 00 offset to library
      dd    guid1,guid2,guid3,guid4 ; 04 128-bit ID (byte reversed)
      endm
 
LIBRARY_EOL macro
      dd    0
      endm
 
BGL_LIBRARY_OBJECT      macro      guid1,guid2,guid3,guid4,power,lsize,scale,ltype,prop,lend,ltitle
      local op_base,start
op_base dd  guid1,guid2,guid3,guid4 ; 00 128-bit ID (byte reversed)
      db    power             ; 16 image power
      dd    (start-op_base)         ; start of the real bglcode
      dd    (lend-start)            ; length of the real bgl code
      dd    lsize             ; size of the object in Meters
      dd    scale             ; scale factor of this object
      dd    ltype             ; library type (current undefined = 0)
      dd    prop              ; library properties (current undefined = 0)
      ifnb  <ltitle>          ; 0 or less than 47 chars
      db    ltitle,0          ; title (may be blank)
      db    ($-(offset op_base)) AND 1 dup (0)
      endif
start  label word
      endm
 
ADDOBJ      macro dest
      local start
start  label word
      dw    32h
      dw    (offset dest)-(offset start)
      ERRS16      (offset dest)-(offset start)
      endm
 
ADDOBJ_32   macro dest
      local start
start  label word
      dw    02Bh
      dd    (offset dest)-(offset start)
      endm
 
INSTANCE_CALL     macro dest,p,b,hh
      local start
start  label word
      dw    033h
      dw    (offset dest)-(offset start)
      dw    p
      dw    b
      dw    hh
      ERRS16      (offset dest)-(offset start)
      endm
 
 
CONCAVE     macro                   ; override the next polygon to be CONCAVE
      dw    038h
      endm
 
BALL  macro size,x,y,z
      dw    028h
      dw    size
      dw    x,y,z
      endm
 
 
IFMSK macro dest,var,mask
      local start
start  label word
      dw    039h
      dw    (offset dest)-(offset start)
      dw    offset var
      dw    mask
      ERRS16      (offset dest)-(offset start)
      endm
 
if_n = 0
if_flag = 0
 
GEN_LABEL macro name, n, s
      &name&_&n label s
endm
 
OFF_LABEL macro name, n, rel, s
      dw (offset &name&_&n - $ - rel) / (s)
endm
 
BGL_IF      macro var,mask
      .errnz if_flag          ; BGL_IF cant nest
      IFMSK if_%(if_n),var,mask
      if_flag = 1
      endm
 
BGL_ELSE    macro
      JUMP if_%(if_n + 1)
      GEN_LABEL if, %(if_n), word
      if_n = if_n + 1
      endm
 
BGL_ENDIF  macro
      GEN_LABEL if, %(if_n), word
      if_n = if_n + 1
      if_flag = 0
      endm
 
; CASE      var_addr,num_cases,case_fall,case_addresses...
;     if [var_address] < num_cases
;           jmp [CASE + 4 + [var_address]*2]
;     else fall through
 
CASE  macro      var_addr,case_fall,c0,c1,c2,c3,c4,c5,c6,c7,c8,c9,c10,c11,c12,c13,c14,c15,c16,c17,c18,c19,c20,c21,c22,c23,c24
      local lbl
lbl   dw    003h
      dw    [(lb3-lb2)/2]
      dw    var_addr
      dw    case_fall-lbl
lb2   label word
      ifnb  <c0>
      dw    c0-lbl
      endif
      ifnb  <c1>
      dw    c1-lbl
      endif
      ifnb  <c2>
      dw    c2-lbl
      endif
      ifnb  <c3>
      dw    c3-lbl
      endif
      ifnb  <c4>
      dw    c4-lbl
      endif
      ifnb  <c5>
      dw    c5-lbl
      endif
      ifnb  <c6>
      dw    c6-lbl
      endif
      ifnb  <c7>
      dw    c7-lbl
      endif
      ifnb  <c8>
      dw    c8-lbl
      endif
      ifnb  <c9>
      dw    c9-lbl
      endif
      ifnb  <c10>
      dw    c10-lbl
      endif
      ifnb  <c11>
      dw    c11-lbl
      endif
      ifnb  <c12>
      dw    c12-lbl
      endif
      ifnb  <c13>
      dw    c13-lbl
      endif
      ifnb  <c14>
      dw    c14-lbl
      endif
      ifnb  <c15>
      dw    c15-lbl
      endif
      ifnb  <c16>
      dw    c16-lbl
      endif
      ifnb  <c17>
      dw    c17-lbl
      endif
      ifnb  <c18>
      dw    c18-lbl
      endif
      ifnb  <c19>
      dw    c19-lbl
      endif
      ifnb  <c20>
      dw    c20-lbl
      endif
      ifnb  <c21>
      dw    c21-lbl
      endif
      ifnb  <c22>
      dw    c22-lbl
      endif
      ifnb  <c23>
      dw    c23-lbl
      endif
      ifnb  <c24>
      dw    c24-lbl
      endif
lb3   label word
      endm
 
 
SCALE macro dest,signal,size,scale,lat,latf,lon,lonf,alt,altf
      local start
start  label word
      dw    02fh
      dw    (offset dest)-(offset start)
      dw    signal
      dw    size
      dw    0                 ; radsort ptr
      dd    scale
      dw    latf
      dd    lat
      dw    lonf
      dd    lon
      dw    altf
      dd    alt
      ERRS16      (offset dest)-(offset start)
      endm
 
 
SUPER_SCALE macro dest,signal,size,scale
      local start
start  label word
      dw    34h
      dw    (offset dest)-(offset start)
      dw    signal
      dw    size
      if    (scale le 31)
            dw    scale
      else
            dw    scale+32
      endif
      ERRS16      (offset dest)-(offset start)
      endm
 
 
SUPER_SCALEV      macro dest,signal,size,scale
      local start
start  label word
      dw    34h
      dw    (offset dest)-(offset start)
      dw    signal
      dw    size
      dw    scale+32
      ERRS16      (offset dest)-(offset start)
      endm
 
 
POSITION    macro dest,signal,size,lat,latf,lon,lonf,alt,altf
      local start
start  label word
      dw    03Ch
      dw    (offset dest)-(offset start)
      dw    signal
      dw    size
      dw    0                 ; radsort ptr
      dw    latf
      dd    lat
      dw    lonf
      dd    lon
      dw    altf
      dd    alt
      ERRS16      (offset dest)-(offset start)
      endm
 
 
VPOSITION   macro dest,signal,size,adrs
      local start
start  label word
      dw    3Ah
      dw    (offset dest)-(offset start)
      dw    signal
      dw    size
      dw    0                 ; radsort ptr
      dw    adrs
      ERRS16      (offset dest)-(offset start)
      endm
 
 
VSCALE      macro dest,signal,size,scale,var
      local start
start  label word
      dw    04ch
      dw    (offset dest)-(offset start)
      dw    signal
      dw    size
      dw    0                 ; radsort ptr
      dd    scale
      dw    var
      ERRS16      (offset dest)-(offset start)
      endm
 
 
VSCALEV macro   dest,psignal,psize,pscale,plla,pnormal
      local start
start  label word
      dw    09Dh
      dw    (offset dest)-(offset start)
      dw    psignal                 ; relative ptr to the signal in params
      dw    psize             ; relative ptr to the size in params
ifnb <pnormal>
      dw    pnormal           ; relative ptr to surface normal
else
      dw    0                 ; no surface normal (was radsort_index)
endif
      dw    pscale                  ; relative ptr to the scale in params
      dw    plla              ; relative ptr to the LATLONALT in params
      ERRS16      (offset dest)-(offset start)
      endm
 
 
VINSTANCE_CALL32  macro dest,var
      local do_jump, done
      VINSTANCE_CALL16 do_jump, var
      JUMP  done
do_jump label word
      BGL_JUMP_32 dest
done  label word
      endm
 
 
VINSTANCE_CALL16  macro dest,var
      local start
start  label word
      dw    03Bh
      dw    (offset dest)-(offset start)
      dw    offset var
      ERRS16      (offset dest)-(offset start)
      endm
 
VINSTANCE_CALL    macro dest,var
    VINSTANCE_CALL16    dest,var
      endm
 
 
SEED  macro type,xsize,zsize,realalt,latgrid,longrid,number
      dw    3dh
      dd    type
      dd    xsize
      dd    zsize
      dd    realalt
      dw    latgrid
      dw    longrid
      dw    number
      endm
 
FACET3      macro a,b,c,d,p1,p2,p3
      dw    3eh,3
      dw    a,b,c
      dd    d
      dw    p1,p2,p3
      endm
 
FACET4      macro a,b,c,d,p1,p2,p3,p4
      dw    3eh,4
      dw    a,b,c
      dd    d
      dw    p1,p2,p3,p4
      endm
 
FACET5      macro a,b,c,d,p1,p2,p3,p4,p5
      dw    3eh,5
      dw    a,b,c
      dd    d
      dw    p1,p2,p3,p4,p5
      endm
 
FACET6      macro a,b,c,d,p1,p2,p3,p4,p5,p6
      dw    3eh,6
      dw    a,b,c
      dd    d
      dw    p1,p2,p3,p4,p5,p6
      endm
 
FACET7      macro a,b,c,d,p1,p2,p3,p4,p5,p6,p7
      dw    3eh,7
      dw    a,b,c
      dd    d
      dw    p1,p2,p3,p4,p5,p6,p7
      endm
 
FACET8      macro a,b,c,d,p1,p2,p3,p4,p5,p6,p7,p8
      dw    3eh,8
      dw    a,b,c
      dd    d
      dw    p1,p2,p3,p4,p5,p6,p7,p8
      endm
 
FACET9      macro a,b,c,d,p1,p2,p3,p4,p5,p6,p7,p8,p9
      dw    3eh,9
      dw    a,b,c
      dd    d
      dw    p1,p2,p3,p4,p5,p6,p7,p8,p9
      endm
 
FACET10     macro a,b,c,d,p1,p2,p3,p4,p5,p6,p7,p8,p9,p10
      dw    3eh,10
      dw    a,b,c
      dd    d
      dw    p1,p2,p3,p4,p5,p6,p7,p8,p9,p10
      endm
 
FACET11     macro a,b,c,d,p1,p2,p3,p4,p5,p6,p7,p8,p9,p10,p11
      dw    3eh,11
      dw    a,b,c
      dd    d
      dw    p1,p2,p3,p4,p5,p6,p7,p8,p9,p10,p11
      endm
 
FACET12     macro a,b,c,d,p1,p2,p3,p4,p5,p6,p7,p8,p9,p10,p11,p12
      dw    3eh,12
      dw    a,b,c
      dd    d
      dw    p1,p2,p3,p4,p5,p6,p7,p8,p9,p10,p11,p12
      endm
 
FACET13     macro a,b,c,d,p1,p2,p3,p4,p5,p6,p7,p8,p9,p10,p11,p12,p13
      dw    3eh,13
      dw    a,b,c
      dd    d
      dw    p1,p2,p3,p4,p5,p6,p7,p8,p9,p10,p11,p12,p13
      endm
 
FACET14     macro a,b,c,d,p1,p2,p3,p4,p5,p6,p7,p8,p9,p10,p11,p12,p13,p14
      dw    3eh,14
      dw    a,b,c
      dd    d
      dw    p1,p2,p3,p4,p5,p6,p7,p8,p9,p10,p11,p12,p13,p14
      endm
 
FACET15     macro a,b,c,d,p1,p2,p3,p4,p5,p6,p7,p8,p9,p10,p11,p12,p13,p14,p15
      dw    3eh,15
      dw    a,b,c
      dd    d
      dw    p1,p2,p3,p4,p5,p6,p7,p8,p9,p10,p11,p12,p13,p14,p15
      endm
 
FACET16     macro a,b,c,d,p1,p2,p3,p4,p5,p6,p7,p8,p9,p10,p11,p12,p13,p14,p15,p16
      dw    3eh,16
      dw    a,b,c
      dd    d
      dw    p1,p2,p3,p4,p5,p6,p7,p8,p9,p10,p11,p12,p13,p14,p15,p16
      endm
 
FACET macro      a,b,c,d,p1,p2,p3,p4,p5,p6,p7,p8,p9,p10,p11,p12,p13,p14,p15,p16,p17,p18,p19,p20,p21,p22,p23,p24,p25,p26,p27,p28,p29,p30,p31,p32,p33,p34,p35
      local lb1,lb2
      dw    03Eh
      dw    [(lb2-lb1)/2]
      dw    a,b,c
      dd    d
lb1   dw    p1,p2,p3
      ifnb  <p4>
      dw    p4
      endif
      ifnb  <p5>
      dw    p5
      endif
      ifnb  <p6>
      dw    p6
      endif
      ifnb  <p7>
      dw    p7
      endif
      ifnb  <p8>
      dw    p8
      endif
      ifnb  <p9>
      dw    p9
      endif
      ifnb  <p10>
      dw    p10
      endif
      ifnb  <p11>
      dw    p11
      endif
      ifnb  <p12>
      dw    p12
      endif
      ifnb  <p13>
      dw    p13
      endif
      ifnb  <p14>
      dw    p14
      endif
      ifnb  <p15>
      dw    p15
      endif
      ifnb  <p16>
      dw    p16
      endif
      ifnb  <p17>
      dw    p17
      endif
      ifnb  <p18>
      dw    p18
      endif
      ifnb  <p19>
      dw    p19
      endif
      ifnb  <p20>
      dw    p20
      endif
      ifnb  <p21>
      dw    p21
      endif
      ifnb  <p22>
      dw    p22
      endif
      ifnb  <p23>
      dw    p23
      endif
      ifnb  <p24>
      dw    p24
      endif
      ifnb  <p25>
      dw    p25
      endif
      ifnb  <p26>
      dw    p26
      endif
      ifnb  <p27>
      dw    p27
      endif
      ifnb  <p28>
      dw    p28
      endif
      ifnb  <p29>
      dw    p29
      endif
      ifnb  <p30>
      dw    p30
      endif
      ifnb  <p31>
      dw    p31
      endif
      ifnb  <p32>
      dw    p32
      endif
      ifnb  <p33>
      dw    p33
      endif
      ifnb  <p34>
      dw    p34
      endif
      ifnb  <p35>
      dw    p35
      endif
lb2   label word
      endm
 
FACETN      macro a,b,c,d,n
      local lb1,lb2
      dw    03Eh
      dw    n
      dw    a,b,c
      dd    d
      endm
 
ALPHA macro acolor
      dw    08Fh
      dd    acolor
      endm
 
VALPHA macro var
      dw    0A4h
      dw    var
      endm
 
ALPHA_FACET macro      acolor,a,b,c,d,p1,p2,p3,p4,p5,p6,p7,p8,p9,p10,p11,p12,p13,p14,p15,p16,p17,p18,p19,p20,p21,p22,p23,p24,p25,p26,p27,p28,p29,p30,p31,p32,p33,p34,p35
      ALPHA acolor
      FACET a,b,c,d,p1,p2,p3,p4,p5,p6,p7,p8,p9,p10,p11,p12,p13,p14,p15,p16,p17,p18,p19,p20,p21,p22,p23,p24,p25,p26,p27,p28,p29,p30,p31,p32,p33,p34,p35
      ALPHA 0
      endm
 
SHADOW_CALL macro routine
      local start
start  label word
      dw    3Fh
      dw    (offset routine)-(offset start)
      ERRS16      (offset routine)-(offset start)
      endm
 
SHADOW_VPOSITION  macro adrs
      dw    40h
      dw    adrs
      endm
 
SHADOW_VICALL32   macro dest,var
      local do_jump, done
      SHADOW_VICALL16 do_jump,var
      JUMP  done
do_jump label word
      BGL_JUMP_32 dest
done  label word
      endm
 
SHADOW_VICALL16   macro dest,var
      local start
start  label word
      dw    041h
      dw    (offset dest)-(offset start)
      dw    offset var
      ERRS16      (offset dest)-(offset start)
      endm
 
SHADOW_VICALL     macro dest,var
    SHADOW_VICALL16         dest,var
      endm
 
POINT_VICALL_32 macro   dest,xx,yy,zz,pp,pv,bb,bv,hh,hv
      local do_jump, done
      POINT_VICALL_16 do_jump,xx,yy,zz,pp,pv,bb,bv,hh,hv
      JUMP  done
do_jump label word
      BGL_JUMP_32 dest
done  label word
      endm
 
POINT_VICALL_16 macro   dest,xx,yy,zz,pp,pv,bb,bv,hh,hv
      local start
start  label word
      dw    046h
      dw    (offset dest)-(offset start)
      dw    xx,yy,zz
      dw    pp,pv,bb,bv,hh,hv
      ERRS16      (offset dest)-(offset start)
      endm
 
POINT_VICALL    macro   dest,xx,yy,zz,pp,pv,bb,bv,hh,hv
      POINT_VICALL_16 dest,xx,yy,zz,pp,pv,bb,bv,hh,hv
      endm
 
; -----------------------------------------------------------------------------
; SPRITE_VICALL - This command will always rotate the object toward the eye. It
;             works as follows:
;             1.  xx,yy,zz are subtracted from current visual_position.x/y/z
;             2.  object is rotated in heading if hh is non-zero and then
;                 hh is added to the new heading
;             3.  hv is gotten if non-zero and added to new heading
;             4.  object is rotated in bank if bb is non-zero and then
;                 bb is added to the new bank
;             5.  bv is gotten if non-zero and added to new bank
;             6.  object is rotated in pitch if pp is non-zero and then
;                 pp is added to the new pitch
;             7.  pv is gotten if non-zero and added to new pitch
;             8.  object is then instanced and displayed
;
; Entry:    subroutine  = relative offset to the BGL subroutine
;           xx,yy,zz    = offset for rotate at
;           pp,bb,hh    = fixed PBH to add to rotated object (each of
;                         these must be non-zero to rotated that axis
;                         toward the eye)
;           pv,bv,hv    = offset into current var block to get pbh to
;                         rotated.  This is done even if the axis is not
;                         rotated to the eye.
; -----------------------------------------------------------------------------
SPRITE_VICALL     macro subroutine,xx,yy,zz,pp,pv,bb,bv,hh,hv
      local start
start  label word
      dw    0A7h
      dw    (offset subroutine)-(offset start)
      dw    xx,yy,zz
      XYZ16 {pp,bb,hh}
      XYZ16 {pv,bv,hv}
      ERRS16      (offset subroutine)-(offset start)
      endm
 
 
PNT   macro x,y,z
      dw    037h
      dw    x,y,z
      endm
 
MAP_SCALE   macro scale
      dw    47h
      dw    scale
      endm
 
VAR_SEG     macro tseg
      dw    48h
      dw    tseg
      endm
 
BLDING      macro n,c,dx,dy,dz,s,x,z
      dw    49h
      dw    n,c,dx,dy,dz,s,x,z
      endm
 
BGL_BUILDING      macro      cat,texture_bottom,texture_window,texture_top,texture_roof,sx,syb,sym,syt,sz,txb,tzb,txm,tym,tzm,txt,tzt
      dw    0A0h        ; opcode
      dw    38          ; total length of this opcode
      dw    cat         ; type of building (square with flat roof, round with flat roof, square with slant roof, ...)
      dw    texture_bottom    ; texture maps to use
      dw    texture_window    ; texture maps to use
      dw    texture_top ; texture maps to use
      dw    texture_roof      ; texture maps to use
      dw    sx          ; size of build in the X axis
      dw    syb         ; size of build in the Y axis of the bottom section
      dw    sym         ; size of build in the Y axis of the middle section
      dw    syt         ; size of build in the Y axis of the top section
      dw    sz          ; size of build in the Z axis
      dw    txb         ; texture index for the bottom section in the X axis
      dw    tzb         ; texture index for the bottom section in the Z axis
      dw    txm         ; texture index for the middle section in the X axis
      dw    tym         ; texture index for the middle section in the Y axis
      dw    tzm         ; texture index for the middle section in the Z axis
      dw    txt         ; texture index for the top section in the X axis
      dw    tzt         ; texture index for the top section in the Z axis
      endm
 
 
BUILDING_RECT_FLAT      macro sx,sz
      dw    0A0h        ; opcode
      dw    42          ; total length of this opcode
      dw    OBJECTOP_BUILD_RECT_FLAT_ROOF       ; type of building
      dw    sx          ; size of build in the X axis
      dw    sz          ; size of build in the Z axis
      endm
 
BUILDING_FLAT_ROOF      macro texroof,txr,tzr
      dw    texroof           ; texture maps to use
      dw    txr         ; texture index for the roof section in the X axis
      dw    tzr         ; texture index for the roof section in the Z axis
      endm
 
 
BUILDING_RECT_PEAK      macro sx,sz
      dw    0A0h        ; opcode
      dw    46          ; total length of this opcode
      dw    OBJECTOP_BUILD_RECT_PEAK_ROOF       ; type of building
      dw    sx          ; size of build in the X axis
      dw    sz          ; size of build in the Z axis
      endm
 
BUILDING_RECT_PEAK_ROOF macro texroof,syr,txr,tyr,tzr
      dw    texroof           ; texture maps to use
      dw    txr         ; texture index for the roof section in the X axis
      dw    tzr         ; texture index for the roof section in the Z axis
      dw    syr         ; size of build in the Y axis of the roof section
      dw    tyr         ; texture index for the roof section in the Y axis
      endm
 
 
BUILDING_RECT_RIDGE     macro sx,sz
      dw    0A0h        ; opcode
      dw    50          ; total length of this opcode
      dw    OBJECTOP_BUILD_RECT_RIDGE_ROOF            ; type of building
      dw    sx          ; size of build in the X axis
      dw    sz          ; size of build in the Z axis
      endm
 
BUILDING_RECT_RIDGE_ROOF      macro texroof,syr,txr,tzr, texgab,txg,tyg
      dw    texroof           ; texture maps to use
      dw    txr         ; texture index for the roof section in the X axis
      dw    tzr         ; texture index for the roof section in the Z axis
 
      dw    syr         ; size of build in the Y axis of the top section
      dw    tyg         ; texture index for the gable section in the Y axis
 
      dw    texgab            ; texture maps to use
      dw    txg         ; texture index for the gable section in the X axis
      endm
 
 
BUILDING_RECT_SLANT     macro sx,sz
      dw    0A0h        ; opcode
      dw    56          ; total length of this opcode
      dw    OBJECTOP_BUILD_RECT_SLANT_ROOF            ; type of building
      dw    sx          ; size of build in the X axis
      dw    sz          ; size of build in the Z axis
      endm
 
BUILDING_RECT_SLANT_ROOF      macro texroof,syr,txr,tzr, texgab,txg,tyg, texface,tzf,tyf
      dw    texroof           ; texture maps to use
      dw    txr         ; texture index for the roof section in the X axis
      dw    tzr         ; texture index for the roof section in the Z axis
 
      dw    syr         ; size of build in the Y axis of the top section
      dw    tyg         ; texture index for the gable section in the Y axis
 
      dw    texgab            ; texture maps to use
      dw    txg         ; texture index for the gable section in the X axis
 
      dw    texface           ; texture maps to use
      dw    tzf         ; texture index for the face section in the Z axis
      dw    tyf         ; texture index for the face section in the Y axis
      endm
 
 
BUILDING_PYRAMID  macro sbx,sbz,stx,stz
      dw    0A0h        ; opcode
      dw    46          ; total length of this opcode
      dw    OBJECTOP_BUILD_PYRAMID        ; type of building
      dw    sbx         ; size of build base in the X axis
      dw    sbz         ; size of build base in the Z axis
      dw    stx         ; size of build top in the X axis
      dw    stz         ; size of build top in the Z axis
      endm
 
 
BUILDING_RECT_BOTTOM    macro texbot,syb,txb,tzb
      dw    texbot            ; texture maps to use
      dw    syb         ; size of build in the Y axis of the bottom section
      dw    txb         ; texture index for the bottom section in the X axis
      dw    tzb         ; texture index for the bottom section in the Z axis
      endm
 
BUILDING_RECT_WINDOW    macro texwin,syw,txw,tyw,tzw
      dw    texwin            ; texture maps to use
      dw    syw         ; size of build in the Y axis of the middle section
      dw    txw         ; texture index for the middle section in the X axis
      dw    tyw         ; texture index for the middle section in the Y axis
      dw    tzw         ; texture index for the middle section in the Z axis
      endm
 
BUILDING_RECT_TOP macro textop,syt,txt,tzt
      dw    textop            ; texture maps to use
      dw    syt         ; size of build in the Y axis of the top section
      dw    txt         ; texture index for the top section in the X axis
      dw    tzt         ; texture index for the top section in the Z axis
      endm
 
 
BUILDING_OCTAGAN  macro sx,sz,sides,smoothing
      dw    0A0h        ; opcode
      dw    40          ; total length of this opcode
      dw    OBJECTOP_BUILD_OCTAGANAL            ; type of building
      db    sides       ; number of sides
      db    smoothing   ; smoothed shading
      dw    sx          ; size of build in the X axis
      dw    sz          ; size of build in the Z axis
      endm
 
 
BUILDING_MULTI_SIDED    macro sx,sz,sides,smoothing
      dw    0A0h        ; opcode
      dw    40          ; total length of this opcode
      dw    OBJECTOP_BUILD_N_SIDED        ; type of building
      db    sides       ; number of sides
      db    smoothing   ; smoothed shading
      dw    sx          ; size of build in the X axis
      dw    sz          ; size of build in the Z axis
      endm
 
 
BUILDING_MULTI_SIDED_WALLS    macro texbot,syb,txb, texwin,syw,txw,tyw, textop,syt,txt
      dw    texbot            ; texture maps to use
      dw    syb         ; size of build in the Y axis of the bottom section
      dw    txb         ; texture index for the bottom section in the X axis
 
      dw    texwin            ; texture maps to use
      dw    syw         ; size of build in the Y axis of the middle section
      dw    txw         ; texture index for the middle section in the X axis
      dw    tyw         ; texture index for the middle section in the Y axis
 
      dw    textop            ; texture maps to use
      dw    syt         ; size of build in the Y axis of the top section
      dw    txt         ; texture index for the top section in the X axis
      endm
 
BUILDING_MULTI_SIDED_ROOF     macro texroof,syr,txr,tzr
      dw    texroof           ; texture maps to use
      dw    syr         ; size of build in the Y axis of the roof section
      dw    txr         ; texture index for the roof section in the X axis
      dw    tzr         ; texture index for the roof section in the Z axis
      endm
 
 
BGL_WINDSOCK      macro biasx,biasy,biasz,height,sock_length,pole_color,sock_color,flags
      dw          0A0h                    ; opcode
      dw          36                            ; total length of this opcode
      dw          OBJECTOP_WINDSOCK ; type of object (521)
      real4 biasx,biasy,biasz ; bias from the current scale command (in scale units)
      real4 height                        ; height of the support pole (in scale units)
      real4 sock_length             ; length of the sock (in scale units)
      dd          pole_color              ; RGBA color of the pole
      dd          sock_color              ; RGBA color of the sock
      dw          flags                   ; general flags, all 0, bit 0 is lighted
      endm
 
 
BGL_EFFECT  macro effect_name, effect_params
      local effect_beg
      local effect_end
      local name_beg
 
effect_beg  label word
      dw    0A0h              ; opcode
      dw    (offset effect_end) - (offset effect_beg)
      dw    OBJECTOP_EFFECT   ; type of object
      dd    0
 
name_beg label word
      db    effect_name
      db    (80 - ($-(offset name_beg))) dup (0)
      ifnb  <effect_params>
      ifdif <effect_params>,<"">
      db    effect_params
      endif
      endif
      db    0
      db    ($-(offset name_beg)) AND 1 dup (0)
 
effect_end  label word
      endm
 
 
LANDING_LIGHTS_VICALL   macro dest,var,lx,ly,lz
      local start
start  label word
      dw    04ah
      dw    (offset dest)-(offset start)
      dw    offset var
      dw    lx
      dw    ly
      dw    lz
      ERRS16      (offset dest)-(offset start)
      endm
 
BGL_OVERLAY macro      id,c0,c1,c2,c3,c4,c5,c6,c7,c8,c9,c10,c11,c12,c13,c14,c15,c16,c17,c18,c19,c20,c21,c22,c23,c24
      local lbl,lbl2
lbl   dw    4Bh
      dw    (lbl2-lbl)
      dw    id
      ifnb  <c0>
      dw    c0
      endif
      ifnb  <c1>
      dw    c1
      endif
      ifnb  <c2>
      dw    c2
      endif
      ifnb  <c3>
      dw    c3
      endif
      ifnb  <c4>
      dw    c4
      endif
      ifnb  <c5>
      dw    c5
      endif
      ifnb  <c6>
      dw    c6
      endif
      ifnb  <c7>
      dw    c7
      endif
      ifnb  <c8>
      dw    c8
      endif
      ifnb  <c9>
      dw    c9
      endif
      ifnb  <c10>
      dw    c10
      endif
      ifnb  <c11>
      dw    c11
      endif
      ifnb  <c12>
      dw    c12
      endif
      ifnb  <c13>
      dw    c13
      endif
      ifnb  <c14>
      dw    c14
      endif
      ifnb  <c15>
      dw    c15
      endif
      ifnb  <c16>
      dw    c16
      endif
      ifnb  <c17>
      dw    c17
      endif
      ifnb  <c18>
      dw    c18
      endif
      ifnb  <c19>
      dw    c19
      endif
      ifnb  <c20>
      dw    c20
      endif
      ifnb  <c21>
      dw    c21
      endif
      ifnb  <c22>
      dw    c22
      endif
      ifnb  <c23>
      dw    c23
      endif
      ifnb  <c24>
      dw    c24
      endif
lbl2  label word
      endm
 
 
VAR2LOW64K  macro d,s
      dw    04dh
      dw    d,s
      endm
 
 
LOW64K2VAR  macro d,s
      dw    04eh
      dw    d,s
      endm
 
 
MOVWRD      macro d,s
      dw    04fh
      dw    d,s
      endm
 
 
GCOLOR      macro color
      dw    50h
      dw    color
      endm
 
 
 
LCOLOR      macro color
      dw    51h
      dw    color
      endm
 
 
SCOLOR      macro color
      dw    52h
      dw    color
      endm
 
 
GCOLOR_ABS  macro color
      dw    53h
      dw    color
      endm
 
 
ASMCALL_32  macro asm_offset
      dw    08Ch
      dd    offset asm_offset
      endm
 
SET_SURFACE_TYPE  macro t,x,z,alt
      dw    055h
      dw    t,x,z,alt
      endm
 
SET_WEATHER macro skip
      local start
start  label word
      dw    056h
      dw    (offset skip)-(offset start)
      ERRS16      (offset skip)-(offset start)
      endm
 
BGL_WEATHER macro type,angle,factor,extra
      dw    057h
      dw    04ch+type*256
      dw    angle
      dw    factor
      dw    extra
      endm
 
TEXTURE_BOUNDS    macro lx,lz,ux,uz
      dw    058h
      dd    lx,lz,ux,uz
      endm
 
VAR_SEG_ID  macro
      dw    059h
      endm
 
SEED_ADDOBJ macro dest
      local start
start  label word
      dw    5Ah
      dw    (offset dest)-(offset start)
      ERRS16      (offset dest)-(offset start)
      endm
 
INDIRECT_CALL     macro var
      dw    5bh
      dw    var
      endm
 
IFSIZEV     macro dest,radius,pixels
      local start
start  label word
      dw    5Fh
      dw    (offset dest)-(offset start)
      dw    radius,pixels
      ERRS16      (offset dest)-(offset start)
      endm
 
 
 
FACE3_TMAP  macro px,py,pz,nx,ny,nz,p1,t1x,t1z,p2,t2x,t2z,p3,t3x,t3z
      dw    60h,3
      dw    px,py,pz,nx,ny,nz
      dw    p1,t1x,t1z
      dw    p2,t2x,t2z
      dw    p3,t3x,t3z
      endm
 
FACE4_TMAP  macro px,py,pz,nx,ny,nz,p1,t1x,t1z,p2,t2x,t2z,p3,t3x,t3z,p4,t4x,t4z
      dw    60h,4
      dw    px,py,pz,nx,ny,nz
      dw    p1,t1x,t1z
      dw    p2,t2x,t2z
      dw    p3,t3x,t3z
      dw    p4,t4x,t4z
      endm
 
FACE7_TMAP  macro      px,py,pz,nx,ny,nz,p1,t1x,t1z,p2,t2x,t2z,p3,t3x,t3z,p4,t4x,t4z,p5,t5x,t5z,p6,t6x,t6z,p7,t7x,t7z
      dw    60h,7
      dw    px,py,pz,nx,ny,nz
      dw    p1,t1x,t1z
      dw    p2,t2x,t2z
      dw    p3,t3x,t3z
      dw    p4,t4x,t4z
      dw    p5,t5x,t5z
      dw    p6,t6x,t6z
      dw    p7,t7x,t7z
      endm
 
 
 
RESLIST_SCALE     macro start,cnt
      dw    61h
      dw    start,cnt
      endm
 
 
 
IFVIS4      macro dest,p1,p2,p3,p4
      local start
start  label word
      dw    62h
      dw    (offset dest)-(offset start)
      dw    4
      dw    p1,p2,p3,p4
      ERRS16      (offset dest)-(offset start)
      endm
 
IFVIS8      macro dest,p1,p2,p3,p4,p5,p6,p7,p8
      local start
start  label word
      dw    62h
      dw    (offset dest)-(offset start)
      dw    8
      dw    p1,p2,p3,p4,p5,p6,p7,p8
      ERRS16      (offset dest)-(offset start)
      endm
 
IFGT  macro dest,var,num
      IFIN1 dest,var,num,32767
      endm
 
IFLT  macro dest,var,num
      IFIN1 dest,var,-32768,num
      endm
 
IFEQ  macro dest,var,num
      IFIN1 dest,var,num,num
      endm
 
PNTROW      macro x1,y1,z1,x2,y2,z2,n
      dw    35h
      dw    x1,y1,z1,x2,y2,z2,n
      endm
 
 
BGL_NEW_RUNWAY    macro name
name  label word
      dw    0AAh
      dw    (offset &name&_end_list - offset name)
      ERRS16      (offset &name&_end_list - offset name)
      endm
 
 
BGL_NEW_RUNWAY_END      macro name
&name&_end_list label word
      endm
 
; RUNWAY_SURFACE must tbe the first subop
RUNWAY_SURFACE    macro      lat,latf,lon,lonf,alt,altf,length,width,heading,flags,ident,lights,surface
      db    01          ; sub-opcode
      dw    latf        ; \ runway center latitude (48-bit meters*65536)
      dd    lat         ; /
      dw    lonf        ; \ runway cneter longitude (48-bit pseudodegrees)
      dd    lon         ; /
      dw    altf        ; \ runway alitude (feet MSL) (48-bit meters*65536)
      dd    alt         ; /
      dw    heading           ; runway true heading (16-bit pseudodegrees)
      dw    length            ; runway length (feet)
      dw    width       ; runway width (feet)
      dw    flags       ; flags
      db    surface           ; surface type
      db    lights            ; edge lights, center lights
      db    ident       ; runway number of designation
      endm
 
 
RUNWAY_BASE_THRESHOLD   macro length
      db    02          ; sub-opcode
      db    0           ; extra spare byte, MUST BE 0
      dw    length            ; length of the threshold (already include in main runway length)
      endm
 
 
RUNWAY_RECIP_THRESHOLD  macro length
      db    03          ; sub-opcode
      db    0           ; extra spare byte, MUST BE 0
      dw    length            ; length of the threshold (already include in main runway length)
      endm
 
 
RUNWAY_BASE_BLAST_PAD   macro length
      db    04          ; sub-opcode
      db    0           ; extra spare byte, MUST BE 0
      dw    length            ; length of the blast pad (NOT include in main runway length)
      endm
 
 
RUNWAY_RECIP_BLAST_PAD  macro length
      db    05          ; sub-opcode
      db    0           ; extra spare byte, MUST BE 0
      dw    length            ; length of the blast pad (NOT include in main runway length)
      endm
 
 
RUNWAY_BASE_APPROACH    macro      flags,approach_type,strobes,vasi_type,vasi_angle,vasi_x,vasi_z,vasi_space
      db    06          ; sub-opcode
      db    0           ; extra spare byte, MUST BE 0
      RUNWAY_LIGHTS      flags,approach_type,strobes,vasi_type,vasi_angle,vasi_x,vasi_z,vasi_space
      endm
 
 
RUNWAY_RECIP_APPROACH   macro      flags,approach_type,strobes,vasi_type,vasi_angle,vasi_x,vasi_z,vasi_space
      db    07          ; sub-opcode
      db    0           ; extra spare byte, MUST BE 0
      RUNWAY_LIGHTS      flags,approach_type,strobes,vasi_type,vasi_angle,vasi_x,vasi_z,vasi_space
      endm
 
 
RUNWAY_BASE_OVERRUN     macro length,width,surface
      db    08          ; sub-opcode
      db    surface           ; surface type  (does NOT have to be the same as the main runway)
      dw    length            ; length of the threshold (already include in main runway length)
      dw    width       ; width (does NOT have to be the same as the main runway)
      endm
 
 
RUNWAY_RECIP_OVERRUN    macro length,width,surface
      db    09          ; sub-opcode
      db    surface           ; surface type  (does NOT have to be the same as the main runway)
      dw    length            ; length of the threshold (already include in main runway length)
      dw    width       ; width (does NOT have to be the same as the main runway)
      endm
 
 
RUNWAY_BASE_DISTANCE    macro x_offset,flags
      db    10          ; sub-opcode
      db    flags       ; flags to tell the type the distance left numbers
      dw    x_offset    ; offset from the center of the runway
      endm
 
 
RUNWAY_RECIP_DISTANCE   macro x_offset,flags
      db    11          ; sub-opcode
      db    flags       ; flags to tell the type the distance left numbers
      dw    x_offset    ; offset from the center of the runway
      endm
 
 
 
TEXTURE_RUNWAY    macro lat,latf,lon,lonf,alt,altf,length,width,heading,flags,ident,surface
      dw    044h
      dw    latf
      dd    lat
      dw    lonf
      dd    lon
      dw    altf
      dd    alt
      dw    heading
      dw    length
      dw    width
      db    flags
      db    ident
      db    0,0
      db    surface
      db    0           ; rw_threshold_flags
      dw    0           ; rw_threshold_south1
      dw    0           ; rw_threshold_south2
      dw    0           ; rw_threshold_north1
      dw    0           ; rw_threshold_north2
      db    0           ; rw_s_light_flags
      db    0           ; rw_s_light_system
      db    0           ; rw_s_light_strobes
      db    0           ; rw_s_light_vasi_type
      dw    0           ; rw_s_light_vasi_angle
      dw    0           ; rw_s_light_vasi_x
      dw    0           ; rw_s_light_vasi_z
      dw    0           ; rw_s_light_vasi_space
      db    0           ; rw_n_light_flags
      db    0           ; rw_n_light_system
      db    0           ; rw_n_light_strobes
      db    0           ; rw_n_light_vasi_type
      dw    0           ; rw_n_light_vasi_angle
      dw    0           ; rw_n_light_vasi_x
      dw    0           ; rw_n_light_vasi_z
      dw    0           ; rw_n_light_vasi_space
      endm
 
 
RUNWAY_COLORS     macro surf,edge,dash,number,touch,fixed,threshold,blast
      dw    surf
      dw    edge
      dw    dash
      dw    number
      dw    touch
      dw    fixed
      dw    threshold
      dw    blast
      endm
 
 
RUNWAY_MAIN macro lat,latf,lon,lonf,alt,altf,length,width,heading,flags,ident,lights,surface
      dw    044h
      dw    latf        ; \ runway center latitude (48-bit meters*65536)
      dd    lat         ; /
      dw    lonf        ; \ runway cneter longitude (48-bit pseudodegrees)
      dd    lon         ; /
      dw    altf        ; \ runway alitude (feet MSL) (48-bit meters*65536)
      dd    alt         ; /
      dw    heading           ; runway true heading (16-bit pseudodegrees)
      dw    length            ; runway length (feet)
      dw    width       ; runway width (feet)
      db    flags       ;
      db    ident       ;
      db    lights            ; edge lights, center lights
      db    0           ; reserved for expansion
      db    surface           ;
      endm
 
 
BGL_RUNWAY  macro      lat,latf,lon,lonf,alt,altf,length,width,heading,flags,ident,lights,surface,custom
      dw    044h
      dw    latf        ; \ runway center latitude (48-bit meters*65536)
      dd    lat         ; /
      dw    lonf        ; \ runway cneter longitude (48-bit pseudodegrees)
      dd    lon         ; /
      dw    altf        ; \ runway alitude (feet MSL) (48-bit meters*65536)
      dd    alt         ; /
      dw    heading           ; runway true heading (16-bit pseudodegrees)
      dw    length            ; runway length (feet)
      dw    width       ; runway width (feet)
      db    flags       ; flags
      db    ident       ;
      db    lights            ; edge lights, center lights
      db    custom            ; custom flags
      db    surface           ; surface type
      endm
 
 
RUNWAY_THRESHOLD macro  flags,s_thr_ofs,s_blast_pad,n_thr_ofs,n_blast_pad
      db    flags       ; threshold_flags
      dw    s_thr_ofs   ; south threshold offset (feet)
      dw    s_blast_pad ; south blast pad size (feet)
      dw    n_thr_ofs   ; north threshold offset (feet)
      dw    n_blast_pad ; north blast pas size (feet)
      endm
 
 
RUNWAY_LIGHTS     macro      flags,approach_type,strobes,vasi_type,vasi_angle,vasi_x,vasi_z,vasi_space
      db    flags       ; light flags
      db    approach_type     ; approach system type
      db    strobes           ; number of strobes
      db    vasi_type   ; VASI type
      dw    vasi_angle  ; VASI angle (16-bit pseudodegrees)
      dw    vasi_x            ; VASI X offset (feet)
      dw    vasi_z            ; VASI Z offset (feet)
      dw    vasi_space  ; VASI spacing between bars (feet)
      endm
 
 
POLYGON_RUNWAY    macro lat,latf,lon,lonf,alt,altf,length,width,heading,flags,ident,surface
      dw    044h
      dw    latf
      dd    lat
      dw    lonf
      dd    lon
      dw    altf
      dd    alt
      dw    heading
      dw    length
      dw    width
      db    flags
      db    ident
      db    0,0
      db    surface
      db    0           ; rw_threshold_flags
      dw    0           ; rw_threshold_south1
      dw    0           ; rw_threshold_south2
      dw    0           ; rw_threshold_north1
      dw    0           ; rw_threshold_north2
      db    0           ; rw_s_light_flags
      db    0           ; rw_s_light_system
      db    0           ; rw_s_light_strobes
      db    0           ; rw_s_light_vasi_type
      dw    0           ; rw_s_light_vasi_angle
      dw    0           ; rw_s_light_vasi_x
      dw    0           ; rw_s_light_vasi_z
      dw    0           ; rw_s_light_vasi_space
      db    0           ; rw_n_light_flags
      db    0           ; rw_n_light_system
      db    0           ; rw_n_light_strobes
      db    0           ; rw_n_light_vasi_type
      dw    0           ; rw_n_light_vasi_angle
      dw    0           ; rw_n_light_vasi_x
      dw    0           ; rw_n_light_vasi_z
      dw    0           ; rw_n_light_vasi_space
      endm
 
 
APPROACH_LIGHTS   macro      delta_z,width,heading,flags,system,strobes,vasi,vasi_angle,vasi_dx,vasi_dz,vasi_space
      dw    072h
      dw    heading
      dw    width
      dw    delta_z
      db    flags
      db    system
      db    strobes
      db    vasi
      dw    vasi_angle
      dw    vasi_dx
      dw    vasi_dz
      dw    vasi_space
      endm
 
 
VSCOLOR     macro var
      dw    65h
      dw    var
      endm
 
VGCOLOR     macro var
      dw    66h
      dw    var
      endm
 
VLCOLOR     macro var
      dw    67h
      dw    var
      endm
 
TMAP_LIGHT_SHADE  macro nx,ny,nz
      dw    68h,nx,ny,nz
      endm
 
ROAD_START  macro width,x,y,z
      dw    69h
      dw    width
      dw    x,y,z
      endm
 
ROAD_CONT   macro x,y,z
      dw    6ah
      dw    x,y,z
      endm
 
RIVER_START macro width,x,y,z
      dw    6bh
      dw    width
      dw    x,y,z
      endm
 
RIVER_CONT  macro x,y,z
      dw    6ch
      dw    x,y,z
      endm
 
 
IFSIZEH     macro dest,radius,pixels
      local start
start  label word
      dw    6Dh
      dw    (offset dest)-(offset start)
      dw    radius,pixels
      ERRS16      (offset dest)-(offset start)
      endm
 
 
TAXIWAY_START     macro width,x,y,z
      dw    6eh
      dw    width
      dw    x,y,z
      endm
 
TAXIWAY_CONT      macro x,y,z
      dw    6fh
      dw    x,y,z
      endm
 
 
 
BGL_TAXI_MARKINGS macro name
name  label word
      dw    01Fh
      dw    (offset &name&_end_list - offset name)
      ERRS16      (offset &name&_end_list - offset name)
      endm
 
 
BGL_TAXI_MARKINGS_END   macro name
&name&_end_list label word
      endm
 
BGL_TAXI_ILS_HOLD macro x1,z1,x2,z2
      dw    TAXI_SUBOPF_ILS_HOLD
      real4 x1,z1
      real4 x2,z2
      endm
 
BGL_TAXI_RUNWAY_HOLD    macro x1,z1,x2,z2
      dw    TAXI_SUBOPF_RUNWAY_HOLD
      real4 x1,z1
      real4 x2,z2
      endm
 
BGL_TAXI_HOLD     macro x1,z1,x2,z2
      dw    TAXI_SUBOPF_TAXI_HOLD
      real4 x1,z1
      real4 x2,z2
      endm
 
BGL_TAXI_SOLID_EDGE     macro x1,z1
      dw    TAXI_SUBOPF_SOLID_SOLID_EDGE
      real4 x1,z1
      endm
 
BGL_TAXI_SPLIT_EDGE     macro x1,z1
      dw    TAXI_SUBOPF_DASHED_SOLID_EDGE
      real4 x1,z1
      endm
 
BGL_TAXI_DASHED_EDGE    macro x1,z1
      dw    TAXI_SUBOPF_DASHED_DASHED_EDGE
      REAL4 x1,z1
      endm
 
BGL_TAXI_ARC      macro
      dw    TAXI_SUBOP_ARC
      endm
 
BGL_TAXI_BREAK    macro
      dw    TAXI_SUBOP_BREAK;
      endm
 
BGL_TAXI_CENTER   macro x1,z1
      dw    TAXI_SUBOPF_CENTER
      REAL4 x1,z1
      endm
 
BGL_TAXI_SOLID_EDGE_LIGHTED   macro x1,z1
      dw    TAXI_SUBOPF_SOLID_SOLID_EDGE_LIGHTED
      REAL4 x1,z1
      endm
 
BGL_TAXI_SPLIT_EDGE_LIGHTED   macro x1,z1
      dw    TAXI_SUBOPF_DASHED_SOLID_EDGE_LIGHTED
      REAL4 x1,z1
      endm
 
BGL_TAXI_DASHED_EDGE_LIGHTED  macro x1,z1
      dw    TAXI_SUBOPF_DASHED_DASHED_EDGE_LIGHTED
      REAL4 x1,z1
      endm
 
BGL_TAXI_CENTER_LIGHTED macro x1,z1
      dw    TAXI_SUBOPF_CENTER_LIGHTED
      REAL4 x1,z1
      endm
 
BGL_TAXI_ARC_LIGHTED    macro
      dw    TAXI_SUBOP_ARC_LIGHTED
      endm
 
 
 
 
BGL_TAXI_INVISIBLE_SOLID_EDGE macro x1,z1
      dw    TAXI_SUBOPF_INVISIBLE_SOLID_SOLID_EDGE
      real4 x1,z1
      endm
 
BGL_TAXI_INVISIBLE_SPLIT_EDGE macro x1,z1
      dw    TAXI_SUBOPF_INVISIBLE_DASHED_SOLID_EDGE
      real4 x1,z1
      endm
 
BGL_TAXI_INVISIBLE_DASHED_EDGE      macro x1,z1
      dw    TAXI_SUBOPF_INVISIBLE_DASHED_DASHED_EDGE
      REAL4 x1,z1
      endm
 
BGL_TAXI_INVISIBLE_CENTER     macro x1,z1
      dw    TAXI_SUBOPF_INVISIBLE_CENTER
      REAL4 x1,z1
      endm
 
 
 
 
 
;&AREA_SENSE4     macro stype,x1,z1,x2,z2,x3,z3,x4,z4
;&    dw    70h,4,stype
;&    dw    x1,z1,x2,z2,x3,z3,x4,z4
;&    endm
 
AREA_SENSE3 macro dest,x1,z1,x2,z2,x3,z3
      local start
start  label word
      dw    70h
      dw    (offset dest)-(offset start)
      dw    3,x1,z1,x2,z2,x3,z3
      ERRS16      (offset dest)-(offset start)
      endm
 
AREA_SENSE4 macro dest,x1,z1,x2,z2,x3,z3,x4,z4
      local start
start  label word
      dw    70h
      dw    (offset dest)-(offset start)
      dw    4,x1,z1,x2,z2,x3,z3,x4,z4
      ERRS16      (offset dest)-(offset start)
      endm
 
AREA_SENSE5 macro dest,x1,z1,x2,z2,x3,z3,x4,z4,x5,z5
      local start
start  label word
      dw    70h
      dw    (offset dest)-(offset start)
      dw    5,x1,z1,x2,z2,x3,z3,x4,z4,x5,z5
      ERRS16      (offset dest)-(offset start)
      endm
 
AREA_SENSE6 macro dest,x1,z1,x2,z2,x3,z3,x4,z4,x5,z5,x6,z6
      local start
start  label word
      dw    70h
      dw    (offset dest)-(offset start)
      dw    6,x1,z1,x2,z2,x3,z3,x4,z4,x5,z5,x6,z6
      ERRS16      (offset dest)-(offset start)
      endm
 
ALTITUDE_SET      macro alt
      dw    71h
      dw    alt
      endm
 
ADDCAT      macro dest,cat
      local start
start  label word
      dw    74h
      dw    (offset dest)-(offset start)
      dw    cat
      ERRS16      (offset dest)-(offset start)
      endm
 
ADDCAT_32   macro dest,cat
      local start
start  label word
      dw    08Bh
      dd    (offset dest)-(offset start)
      dw    cat
      endm
 
ELEVATION_MAP     macro g_x, g_y, p_x, p_y, d_x, d_y, minalt, maxalt
      dw    15h
      dw    g_x, g_y, p_x, p_y, d_x, d_y, minalt, maxalt
      endm
 
ELEVATION_POINT macro x, z, alt
      db    x, z
      dw    alt
      endm
 
TILED_ELEVATION_MAP     macro g_x, g_y, p_x, p_y, d_x, d_y, minalt, maxalt, texture_min_u, texture_min_v, texture_delta_u, texture_delta_v, tile_algorithm, use_variations
      dw    9Ah
      dw    g_x, g_y, p_x, p_y, d_x, d_y, minalt, maxalt
;assert texture deltas < 16385
;assert tiling algorithm < 16
      db    texture_min_u, texture_min_v
IFNB  <use_variations>
      dd    (texture_delta_u * 262144) + (texture_delta_v * 16) + (tile_algorithm * 2) + use_variations
ELSE
      dd    (texture_delta_u * 262144) + (texture_delta_v * 16) + (tile_algorithm * 2)
ENDIF
      endm
 
TILED_CLASSIFICATION_ELEVATION_MAP  macro g_x, g_y, p_x, p_y, d_x, d_y, minalt, maxalt, texture_min_u, texture_min_v, texture_delta_u, texture_delta_v, tile_algorithm
      local start
start  label word
      dw    0A3h
      dw    g_x, g_y, p_x, p_y, d_x, d_y, minalt, maxalt
;assert texture deltas < 16385
;assert tiling algorithm < 16
      db    texture_min_u, texture_min_v
      dd    (texture_delta_u * 262144) + (texture_delta_v * 16) + (tile_algorithm * 2) + 1 ; + TEXTURE_VARIATIONS - always use variations
 
      endm
 
TILED_ELEVATION_POINT   macro alt
      dw    alt
      endm
 
START_CLASSIFICATION_DATA     macro
      classification_data_start = $
      endm
 
CLASSIFICATION    macro class0, class1, class2, class3, class4, class5, class6, class7, class8, class9, class10, class11, class12, class13, class14, class15
      db    class0
      IFNB  <class1>
      db    class1
      ENDIF
      IFNB  <class2>
      db    class2
      ENDIF
      IFNB  <class3>
      db    class3
      ENDIF
      IFNB  <class4>
      db    class4
      ENDIF
      IFNB  <class5>
      db    class5
      ENDIF
      IFNB  <class6>
      db    class6
      ENDIF
      IFNB  <class7>
      db    class7
      ENDIF
      IFNB  <class8>
      db    class8
      ENDIF
      IFNB  <class9>
      db    class9
      ENDIF
      IFNB  <class10>
      db    class10
      ENDIF
      IFNB  <class11>
      db    class11
      ENDIF
      IFNB  <class12>
      db    class12
      ENDIF
      IFNB  <class13>
      db    class13
      ENDIF
      IFNB  <class14>
      db    class14
      ENDIF
      IFNB  <class15>
      db    class15
      ENDIF
      endm
 
END_CLASSIFICATION_DATA       macro
      IF    (classification_data_start - $) AND 1
      db    0
      %out  ADDED PADDING TO CLASSIFICATION DATA
      ENDIF
      endm
 
SET_CLASSIFICATION_LIST_ENTRY macro index, surface_type, texture_list_ptr
      local start
start label word
      dw    0a1h
      dw    index
      db    surface_type
      db    0                 ; padding?
      dd    (offset texture_list_ptr)-(offset start)
      endm
 
SET_CURRENT_VARIATION_FROM_CLASSIFICATION macro index
      dw    0a5h
      dw    index
      endm
 
SET_CURRENT_VARIATION_TEXTURE_LIST  macro surface_type, texture_list_ptr
      local start
start label word
      dw    0a2h
      db    surface_type
      db    0                 ; padding?
      dd    (offset texture_list_ptr)-(offset start)
      endm
 
ADDMTN      macro dest
      local start
start  label word
      dw    75h
      dw    (offset dest)-(offset start)
      ERRS16      (offset dest)-(offset start)
      endm
 
 
SCALE_AGL   macro dest,signal,size,scale,lat,latf,lon,lonf,alt,altf
      local start
start  label word
      dw    077h
      dw    (offset dest)-(offset start)
      dw    signal
      dw    size
      dw    0                 ; radsort ptr
      dd    scale
      dw    latf
      dd    lat
      dw    lonf
      dd    lon
      dw    altf              ; dummy altitude to be filled in by
      dd    alt               ; command itself
      ERRS16      (offset dest)-(offset start)
      endm
 
 
ROAD_CONTW  macro w,x,y,z
      dw    78h
      dw    w,x,y,z
      endm
 
RIVER_CONTW macro w,x,y,z
      dw    79h
      dw    w,x,y,z
      endm
 
GFACET3_TMAP      macro a,b,c,d,p1,t1x,t1z,p2,t2x,t2z,p3,t3x,t3z
      dw    7Ah,3
      dw    a,b,c
      dd    d
      dw    p1,t1x,t1z
      dw    p2,t2x,t2z
      dw    p3,t3x,t3z
      endm
 
GFACET4_TMAP      macro a,b,c,d,p1,t1x,t1z,p2,t2x,t2z,p3,t3x,t3z,p4,t4x,t4z
      dw    7Ah,4
      dw    a,b,c
      dd    d
      dw    p1,t1x,t1z
      dw    p2,t2x,t2z
      dw    p3,t3x,t3z
      dw    p4,t4x,t4z
      endm
 
GFACET5_TMAP      macro a,b,c,d,p1,t1x,t1z,p2,t2x,t2z,p3,t3x,t3z,p4,t4x,t4z,p5,t5x,t5z
      dw    7Ah,5
      dw    a,b,c
      dd    d
      dw    p1,t1x,t1z
      dw    p2,t2x,t2z
      dw    p3,t3x,t3z
      dw    p4,t4x,t4z
      dw    p5,t5x,t5z
      endm
 
GFACET6_TMAP      macro      a,b,c,d,p1,t1x,t1z,p2,t2x,t2z,p3,t3x,t3z,p4,t4x,t4z,p5,t5x,t5z,p6,t6x,t6z
      dw    7Ah,6
      dw    a,b,c
      dd    d
      dw    p1,t1x,t1z
      dw    p2,t2x,t2z
      dw    p3,t3x,t3z
      dw    p4,t4x,t4z
      dw    p5,t5x,t5z
      dw    p6,t6x,t6z
      endm
 
GFACET7_TMAP      macro      a,b,c,d,p1,t1x,t1z,p2,t2x,t2z,p3,t3x,t3z,p4,t4x,t4z,p5,t5x,t5z,p6,t6x,t6z,p7,t7x,t7z
      dw    7Ah,7
      dw    a,b,c
      dd    d
      dw    p1,t1x,t1z
      dw    p2,t2x,t2z
      dw    p3,t3x,t3z
      dw    p4,t4x,t4z
      dw    p5,t5x,t5z
      dw    p6,t6x,t6z
      dw    p7,t7x,t7z
      endm
 
GFACET8_TMAP      macro      a,b,c,d,p1,t1x,t1z,p2,t2x,t2z,p3,t3x,t3z,p4,t4x,t4z,p5,t5x,t5z,p6,t6x,t6z,p7,t7x,t7z,p8,t8x,t8z
      dw    7Ah,8
      dw    a,b,c
      dd    d
      dw    p1,t1x,t1z
      dw    p2,t2x,t2z
      dw    p3,t3x,t3z
      dw    p4,t4x,t4z
      dw    p5,t5x,t5z
      dw    p6,t6x,t6z
      dw    p7,t7x,t7z
      dw    p8,t8x,t8z
      endm
 
GFACET9_TMAP      macro      a,b,c,d,p1,t1x,t1z,p2,t2x,t2z,p3,t3x,t3z,p4,t4x,t4z,p5,t5x,t5z,p6,t6x,t6z,p7,t7x,t7z,p8,t8x,t8z,p9,t9x,t9z
      dw    7Ah,9
      dw    a,b,c
      dd    d
      dw    p1,t1x,t1z
      dw    p2,t2x,t2z
      dw    p3,t3x,t3z
      dw    p4,t4x,t4z
      dw    p5,t5x,t5z
      dw    p6,t6x,t6z
      dw    p7,t7x,t7z
      dw    p8,t8x,t8z
      dw    p9,t9x,t9z
      endm
 
GFACET10_TMAP     macro      a,b,c,d,p1,t1x,t1z,p2,t2x,t2z,p3,t3x,t3z,p4,t4x,t4z,p5,t5x,t5z,p6,t6x,t6z,p7,t7x,t7z,p8,t8x,t8z,p9,t9x,t9z,p10,t10x,t10z
      dw    7Ah,10
      dw    a,b,c
      dd    d
      dw    p1,t1x,t1z
      dw    p2,t2x,t2z
      dw    p3,t3x,t3z
      dw    p4,t4x,t4z
      dw    p5,t5x,t5z
      dw    p6,t6x,t6z
      dw    p7,t7x,t7z
      dw    p8,t8x,t8z
      dw    p9,t9x,t9z
      dw    p10,t10x,t10z
      endm
 
GFACET11_TMAP     macro      a,b,c,d,p1,t1x,t1z,p2,t2x,t2z,p3,t3x,t3z,p4,t4x,t4z,p5,t5x,t5z,p6,t6x,t6z,p7,t7x,t7z,p8,t8x,t8z,p9,t9x,t9z,p10,t10x,t10z,p11,t11x,t11z
      dw    7Ah,11
      dw    a,b,c
      dd    d
      dw    p1,t1x,t1z
      dw    p2,t2x,t2z
      dw    p3,t3x,t3z
      dw    p4,t4x,t4z
      dw    p5,t5x,t5z
      dw    p6,t6x,t6z
      dw    p7,t7x,t7z
      dw    p8,t8x,t8z
      dw    p9,t9x,t9z
      dw    p10,t10x,t10z
      dw    p11,t11x,t11z
      endm
 
GFACET12_TMAP     macro      a,b,c,d,p1,t1x,t1z,p2,t2x,t2z,p3,t3x,t3z,p4,t4x,t4z,p5,t5x,t5z,p6,t6x,t6z,p7,t7x,t7z,p8,t8x,t8z,p9,t9x,t9z,p10,t10x,t10z,p11,t11x,t11z,p12,t12x,t12z
      dw    7Ah,12
      dw    a,b,c
      dd    d
      dw    p1,t1x,t1z
      dw    p2,t2x,t2z
      dw    p3,t3x,t3z
      dw    p4,t4x,t4z
      dw    p5,t5x,t5z
      dw    p6,t6x,t6z
      dw    p7,t7x,t7z
      dw    p8,t8x,t8z
      dw    p9,t9x,t9z
      dw    p10,t10x,t10z
      dw    p11,t11x,t11z
      dw    p12,t12x,t12z
      endm
 
GFACET13_TMAP     macro      a,b,c,d,p1,t1x,t1z,p2,t2x,t2z,p3,t3x,t3z,p4,t4x,t4z,p5,t5x,t5z,p6,t6x,t6z,p7,t7x,t7z,p8,t8x,t8z,p9,t9x,t9z,p10,t10x,t10z,p11,t11x,t11z,p12,t12x,t12z,p13,t13x,t13z
      dw    7Ah,13
      dw    a,b,c
      dd    d
      dw    p1,t1x,t1z
      dw    p2,t2x,t2z
      dw    p3,t3x,t3z
      dw    p4,t4x,t4z
      dw    p5,t5x,t5z
      dw    p6,t6x,t6z
      dw    p7,t7x,t7z
      dw    p8,t8x,t8z
      dw    p9,t9x,t9z
      dw    p10,t10x,t10z
      dw    p11,t11x,t11z
      dw    p12,t12x,t12z
      dw    p13,t13x,t13z
      endm
 
GFACET14_TMAP     macro      a,b,c,d,p1,t1x,t1z,p2,t2x,t2z,p3,t3x,t3z,p4,t4x,t4z,p5,t5x,t5z,p6,t6x,t6z,p7,t7x,t7z,p8,t8x,t8z,p9,t9x,t9z,p10,t10x,t10z,p11,t11x,t11z,p12,t12x,t12z,p13,t13x,t13z,p14,t14x,t14z
      dw    7Ah,14
      dw    a,b,c
      dd    d
      dw    p1,t1x,t1z
      dw    p2,t2x,t2z
      dw    p3,t3x,t3z
      dw    p4,t4x,t4z
      dw    p5,t5x,t5z
      dw    p6,t6x,t6z
      dw    p7,t7x,t7z
      dw    p8,t8x,t8z
      dw    p9,t9x,t9z
      dw    p10,t10x,t10z
      dw    p11,t11x,t11z
      dw    p12,t12x,t12z
      dw    p13,t13x,t13z
      dw    p14,t14x,t14z
      endm
 
GFACETN_TMAP      macro      a,b,c,d,p1,t1x,t1z,p2,t2x,t2z,p3,t3x,t3z,p4,t4x,t4z,p5,t5x,t5z,p6,t6x,t6z,p7,t7x,t7z,p8,t8x,t8z,p9,t9x,t9z,p10,t10x,t10z,p11,t11x,t11z,p12,t12x,t12z,p13,t13x,t13z,p14,t14x,t14z
      local lb1,lb2
      dw    7Ah
      dw    [(lb2-lb1)/6]
      dw    a,b,c
      dd    d
lb1   dw    p1,t1x,t1z
      dw    p2,t2x,t2z
      dw    p3,t3x,t3z
      ifnb  <p4>
      dw    p4,t4x,t4z
      endif
      ifnb  <p5>
      dw    p5,t5x,t5z
      endif
      ifnb  <p6>
      dw    p6,t6x,t6z
      endif
      ifnb  <p7>
      dw    p7,t7x,t7z
      endif
      ifnb  <p8>
      dw    p8,t8x,t8z
      endif
      ifnb  <p9>
      dw    p9,t9x,t9z
      endif
      ifnb  <p10>
      dw    p10,t10x,t10z
      endif
      ifnb  <p11>
      dw    p11,t11x,t11z
      endif
      ifnb  <p12>
      dw    p12,t12x,t12z
      endif
      ifnb  <p13>
      dw    p13,t13x,t13z
      endif
      ifnb  <p14>
      dw    p14,t14x,t14z
      endif
lb2   label word
      endm
 
 
 
GFACE4_TMAP macro px,py,pz,nx,ny,nz,p1,t1x,t1z,p2,t2x,t2z,p3,t3x,t3z,p4,t4x,t4z
      dw    7bh,4
      dw    px,py,pz,nx,ny,nz
      dw    p1,t1x,t1z
      dw    p2,t2x,t2z
      dw    p3,t3x,t3z
      dw    p4,t4x,t4z
      endm
 
 
;&POLYLINE_FACET  macro      a,b,c,d,p1,p2,p3,p4,p5,p6,p7,p8,p9,p10,p11,p12,p13,p14,p15,p16,p17,p18,p19,p20,p21,p22,p23,p24,p25,p26,p27,p28,p29,p30,p31,p32
;&    local lb1,lb2
;&    dw      07ch
;&    dw      [(lb2-lb1)/2]
;&    dw      a,b,c
;&    dd      d
;&lb1 dw      p1,p2,p3
;&    ifnb    <p4>
;&    dw      p4
;&    endif
;&    ifnb    <p5>
;&    dw      p5
;&    endif
;&    ifnb    <p6>
;&    dw      p6
;&    endif
;&    ifnb    <p7>
;&    dw      p7
;&    endif
;&    ifnb    <p8>
;&    dw      p8
;&    endif
;&    ifnb    <p9>
;&    dw      p9
;&    endif
;&    ifnb    <p10>
;&    dw      p10
;&    endif
;&    ifnb    <p11>
;&    dw      p11
;&    endif
;&    ifnb    <p12>
;&    dw      p12
;&    endif
;&    ifnb    <p13>
;&    dw      p13
;&    endif
;&    ifnb    <p14>
;&    dw      p14
;&    endif
;&    ifnb    <p15>
;&    dw      p15
;&    endif
;&    ifnb    <p16>
;&    dw      p16
;&    endif
;&    ifnb    <p17>
;&    dw      p17
;&    endif
;&    ifnb    <p18>
;&    dw      p18
;&    endif
;&    ifnb    <p19>
;&    dw      p19
;&    endif
;&    ifnb    <p20>
;&    dw      p20
;&    endif
;&    ifnb    <p21>
;&    dw      p21
;&    endif
;&    ifnb    <p22>
;&    dw      p22
;&    endif
;&    ifnb    <p23>
;&    dw      p23
;&    endif
;&    ifnb    <p24>
;&    dw      p24
;&    endif
;&    ifnb    <p25>
;&    dw      p25
;&    endif
;&    ifnb    <p26>
;&    dw      p26
;&    endif
;&    ifnb    <p27>
;&    dw      p27
;&    endif
;&    ifnb    <p28>
;&    dw      p28
;&    endif
;&    ifnb    <p29>
;&    dw      p29
;&    endif
;&    ifnb    <p30>
;&    dw      p30
;&    endif
;&    ifnb    <p31>
;&    dw      p31
;&    endif
;&    ifnb    <p32>
;&    dw      p32
;&    endif
;&lb2 label word
;&    endm
 
PERSPECTIVE macro
      dw    07dh
      endm
 
SETWRD_LOW64K     macro v,n
      dw    7eh,v,n
      endm
 
CITY  macro
      dw    07fh
      endm
 
RESPNT      macro n
      dw    080h,n
      endm
 
ANTI_ALIAS  macro parm
      dw    081h,parm
      endm
 
SHADOW_POSITION   macro lat,latf,lon,lonf,alt,altf
      dw    082h
      dw    latf
      dd    lat
      dw    lonf
      dd    lon
      dw    altf
      dd    alt
      endm
 
RESCALE     macro dest,signal,size,factor
      local start
start  label word
      dw    083h
      dw    (offset dest)-(offset start)
      dw    signal
      dw    size
      dd    factor
      ERRS16      (offset dest)-(offset start)
      endm
 
SURFACE_NORMAL    macro nx,ny,nz
      dw    084h
      dw    nx,ny,nz
      endm
 
NIGHT_COLOR_RANGE macro n
      dw    087h,n
      endm
 
; obsolete w/version 6.x
;FILE_MARKER      macro fileno
;     dw    088h,fileno
;     endm
 
FILE_MARKER_32    macro fileno
      dw    08Dh
      dd    fileno
      endm
 
VFILE_MARKER      macro vfileno
      dw    08Eh, vfileno
      endm
 
;& MOVED CATEGORY DEFINES TO BGLDEF.H
;&CAT_MESH  equ   4
;&CAT_POLY  equ   8
;&CAT_RIVER equ   12
;&CAT_ROAD  equ   16
;&CAT_LINE  equ   20
;&CAT_RUNWAY      equ   24
;&CAT_MOUNTAIN    equ   28
;&CAT_SHADOWS     equ   60
 
 
;;SURFACE_CONCRETE      equ   0
;;SURFACE_GRASS         equ   1
;;SURFACE_WATER         equ   2
 
; Scale factors in ii.ff units per meters, S_16 = 1 unit/meter
S_6         equ 67108864
S_7         equ   33554432
S_8         equ   16777216
S_9         equ   8388608
S_10  equ   4194304
S_11  equ   2097152
S_12  equ   1048576
S_13  equ   524288
S_14  equ   262144
S_15  equ   131072
S_16  equ   65536
S_17  equ   32767
S_18  equ   16384
S_19  equ   8192
S_20  equ   4096
S_21  equ   2048
S_22  equ   1024
S_23  equ   512
S_24  equ   256
 
 
 
PVICALL     macro dest,xvar,yvar,zvar,pp,pv,bb,bv,hh,hv
      local start
      movwrd      start+4,xvar
      movwrd      start+6,yvar
      movwrd      start+8,zvar
start  label word
      dw    046h
      dw    (offset dest)-(offset start)
      dw    0,0,0
      dw    pp,pv,bb,bv,hh,hv
      ERRS16      (offset dest)-(offset start)
      endm
 
GENERIC_FUEL_BOX  macro
      local object_end
 
      LCOLOR      C_YELLOW
      SET_BRIGHTNESS 07FFFh
 
      SPNT  -128,0,-188
      CPNT  -128,0,152
      CPNT  176,0,152
      SPNT  122,0,-12
      CPNT  -128,0,-12
 
; refueling ramp
      SPNT  -261,0,-261
      CPNT  249,0,-261
      CPNT  249,0,257
      CPNT  -261,0,257
      CPNT  -261,0,-261
 
      IFIN1 object_end,xv,-261,255
      IFIN1 object_end,zv,-261,257
 
      setwrd      rpfuel,1
 
object_end  label word
      endm
 
GENERIC_TOWER     macro
      local      shadow_me,tower_top,tower_base,tower_top1,tower_light,beacon_white,beacon_on,beacon_off
 
xsize = 5
ysize = 10
tysize = 12
txsize = 6
 
      SHADOW_CALL shadow_me
shadow_me  label word
 
      RESLIST     0,12
      VERTEX      0,0,0
      VERTEX      xsize,0,0
      VERTEX      xsize,0,xsize
      VERTEX      0,0,xsize
      VERTEX      0,ysize,0
      VERTEX      xsize,ysize,0
      VERTEX      xsize,ysize,xsize
      VERTEX      0,ysize,xsize
      VERTEX      (xsize-txsize),tysize,(xsize-txsize)
      VERTEX      txsize,tysize,(xsize-txsize)
      VERTEX      txsize,tysize,txsize
      VERTEX      (xsize-txsize),tysize,txsize
 
      IFSIDE            0,32767,0,327670, TOWER_BASE, TOWER_TOP
 
TOWER_TOP  label word
      IFSIDE      0,1,0,tysize,TOWER_TOP1,TOWER_LIGHT
 
TOWER_BASE  label word
      SCOLOR      c_white
; south wall
      FACET4      0,0,-32767,0,1,0,4,5
; east wall
      FACET4      32767,0,0,163835,2,1,5,6
; north wall
      FACET4      0,0,32767,163835,3,2,6,7
; west wall
      FACET4      -32767,0,0,0,0,3,7,4
; top of the base
      FACET4      0,32767,0,327670,7,6,5,4
 
      BGL_RETURN
 
 
TOWER_TOP1  label word
 
; inside top
      SCOLOR      c_gray
      FACE4 0,tysize,0,0,-32767,0,8,9,10,11
 
; lines for glass
      LCOLOR      c_black
 
      STRRES      4
      CNTRES      8
      STRRES      5
      CNTRES      9
      STRRES      6
      CNTRES      10
      STRRES      7
      CNTRES      11
 
; outside top
      SCOLOR      c_black
      FACE4 0,tysize,0,0,32767,0,11,10,9,8
 
      BGL_RETURN
 
TOWER_LIGHT  label word
      IFMSK beacon_white,beacnt,3
      LCOLOR      C_BRIGHT_GREEN
      JUMP  beacon_on
 
BEACON_WHITE  label word
      IFMSK beacon_off,beacnt,0300h
      LCOLOR      C_BRIGHT_WHITE
 
BEACON_ON  label word
      PNT   xsize/2,tysize,xsize/2
 
BEACON_OFF  label word
      BGL_RETURN
 
 
      endm
 
 
GENERIC_BEACON    macro
      local beacon_white,beacon_on,beacon_off
 
      IFMSK beacon_white,beacnt,3
      LCOLOR      C_BRIGHT_GREEN
      JUMP  beacon_on
 
BEACON_WHITE  label word
      IFMSK beacon_off,beacnt,0300h
      LCOLOR      C_BRIGHT_WHITE
 
BEACON_ON  label word
      PNT   0,0,0
 
BEACON_OFF  label word
      endm
 
 
;; MOVED TO BGLDEF.H
;;VAR_BASE_PARAMS equ   -1          ; sets varbase to previous PARAMS value
;;VAR_BASE_GLOBAL equ   0           ; sets varbase to GLOBAL
;;VAR_BASE_LOCAL  equ   1           ; sets varbase to previous LOCAL value
 
VAR_BASE_32 macro abso_base_addr
      dw    89h
      dd    abso_base_addr
      endm
 
 
LOCAL_BASE_32     macro local_offset
      local opcode_base
opcode_base label word
      dw    89h
      dd    (offset local_offset - offset opcode_base)
;     ERRS16      (offset local_offset)-(offset opcode_base)
      endm
 
 
VAR_BASE_OVERRIDE macro abs_base_addr     ; override the next getvar
      dw    9Fh
      dd    abs_base_addr
      endm
 
 
LOCAL_VARS  macro name              ; defines a start of local variables
      local jump1
      jump  (&name&_end_list)
      .errnz      ((offset (&name&_end_list) - offset &name&) AND 000000001h)
name  label word
      endm
 
LOCAL_VARS_END    macro name
&name&_end_list label word
      endm
 
 
BGL_INTERPOLATE   macro input_base,input_ofs,output_base,output_ofs,table_base,table_ofs
      dw    09Eh                    ; opcode = BGLOP_INTERPOLATE = 09Eh
      dd    input_base              ; var_base_32 of input
      dw    input_ofs               ; variables offset to add to var_base
      dd    output_base             ; var_base_32 of output
      dw    output_ofs              ; variables offset to add to var_base
      dd    table_base              ; var_base_32 of table
      dw    table_ofs               ; variables offset to add to var_base
      ERRS16      (input_ofs)
      ERRS16      (output_ofs)
      ERRS16      (table_ofs)
      endm
 
BGL_ANIMATE macro input_base,input_ofs,table_base,table_ofs,xlate_x,xlate_y,xlate_z
      local start
start  label word
      dw    0ADh                    ; opcode = BGLOP_ANIMATE = 0ADh
      dd    input_base              ; var_base_32 of input
      dd    input_ofs               ; variables offset to add to var_base
      dd    table_base              ; var_base_32 of table
      dd    table_ofs               ; variables offset to add to var_base
      real4 xlate_x,xlate_y,xlate_z; fixed translation
      endm
 
BGL_TRANSFORM_END macro
      dw    0AEh
      endm
 
BGL_TRANSFORM_MAT macro in_x,in_y,in_z, m00,m01,m02, m10,m11,m12, m20,m21,m22
      dw    0AFh                   ; opcode = BGL_GET_FLOAT_VALUE
      real4 in_x, in_y, in_z  ; xyz translation
      real4 m00, m01, m02     ; 3x3 matrix
      real4 m10, m11, m12     ; 3x3 matrix
      real4 m20, m21, m22     ; 3x3 matrix
      endm
 
 
BGL_TAG     macro in_str
      local str
      dw    0B1h
      str byte in_str
      byte (16-sizeof str) dup (0)
      .errnz      ((15-sizeof str) AND 0FFFF0000h)
      real4   0.0
      endm
 
BGL_FTAG macro in_str, in_flt
      local str
      dw    0B1h
      str byte in_str
      byte (16-sizeof str) dup (0)
      .errnz      ((15-sizeof str) AND 0FFFF0000h)
      real4   in_flt
      endm
 
MIPMAP      macro mipmap_enable
      dw    92h
      dw    mipmap_enable
      endm
 
SPECULAR    macro specular_value
            dw    93h
            dw    specular_value
            endm
 
BGL_TEXT macro    x,y,z,text_handle,text_flags
      dw    091h
      dw    x,y,z,text_handle,text_flags
      endm
 
BGL_AIRCRAFT_LABEL macro      x,y,z,text_handle,text_flags
      dw    091h
      dw    x,y,z,text_handle,text_flags
      endm
 
CRASH_FLAG_NONE               equ   00    ; NOTE:  THESE ENUMS ARE ALSO DEFINED
CRASH_FLAG_MOUNTAIN           equ   02    ;     IN INCLUDE\FS6DEF.H AND MUST
CRASH_FLAG_GENERAL            equ   04    ;     BE CHANGED IN BOTH PLACES
CRASH_FLAG_BUILDING_EYE       equ   06    ; based on eye position
CRASH_FLAG_SPLASH       equ   08
CRASH_FLAG_GEAR_UP            equ   10
CRASH_FLAG_OVERSTRESS         equ   12
CRASH_FLAG_BUILDING_PLANE     equ   14    ; based on plane position
CRASH_FLAG_AIRCRAFT           equ   16
CRASH_FLAG_FUEL_TRUCK         equ   18
CRASH_FLAG_OBJECT       equ   20
 
 
BGL_CRASH   macro density,radius,crash_end,scale,instance
      local start
start label word
      ENUM16      094h
      dw    (offset crash_end)-(offset start)   ; length of the crash code
      dw    radius                              ; 2D radius for grid overlap                    ; radius in Meters
      dw    (offset scale)-(offset start)       ; relative offset to the scale command
      dw    (offset instance)-(offset start)    ; relative offset to the instance command
      db    FALSE                         ; processed flag
      db    density
      ERRS16      (offset crash_end)-(offset start)
      ERRS16      (offset scale)-(offset start)
      ERRS16      (offset instance)-(offset start)
      endm
 
 
BGL_CRASH_INDIRECT      macro density,call_ofs,scale,instance
      local start
start  label word
      ENUM16      095h
      dw    (offset call_ofs)-(offset start)    ; relative offset to the library_call or BGL_CALL
      dw    (offset scale)-(offset start)       ; relative offset to the scale command
;     IF    (instance eq 0 )
;           dw    0
      IFNB  <instance>
            dw    (offset instance)-(offset start); relative offset to the instance command
            ERRS16      (offset instance)-(offset start)
      ELSE
            dw    0
      ENDIF
      db    FALSE                         ; processed flag
      db    density
      ERRS16      (offset call_ofs)-(offset start)
      ERRS16      (offset scale)-(offset start)
      endm
 
 
BGL_CRASH_START   macro crash_end,radius
      local start
start label word
      dw    096h
      dw    (offset crash_end)-(offset start)   ; length of the crash code
      dw    radius                              ; 2D radius for grid overlap                    ; radius in Meters
      ERRS16      (offset crash_end)-(offset start)
      endm
 
 
 
BGL_CRASH_SPHERE  macro fail,radius
      local start
start  label word
      ENUM16      097h
      dw    (offset fail)-(offset start)        ; relative offset to the library call
      dw    radius                              ; radius in Meters
      ERRS16      (offset fail)-(offset start)
      endm
 
BGL_CRASH_BOX     macro fail,centerdx,centerdy,centerdz,sizex,sizey,sizez,pitch,bank,heading
      local start
start  label word
      ENUM16      098h
      dw    (offset fail)-(offset start)        ; relative offset to the library call
      XYZ16 {centerdx,centerdy,centerdz}        ; box center offset from the scale command
      XYZ16 {sizex,sizey,sizez}                 ; rotated size of the box
      PBH16 {pitch,bank,heading}                ; box rotation
      ERRS16      (offset fail)-(offset start)
      endm
 
BGL_CRASH_OCTTREE macro end_label
      local     start
start label word
      dw    BGLOP_CRASH_OCTTREE
      dw    (offset end_label)-(offset start)   ; length of the octtree code
      ERRS16      (offset end_label)-(offset start)
      endm
 
OCTTREE_NODE macro cell0, cell1, cell2, cell3, cell4, cell5, cell6, cell7
      db  cell0, cell1, cell2, cell3, cell4, cell5, cell6, cell7
      endm
 
BGL_SET_CRASH     macro crash_type
      ENUM16      099h
      ENUM16      crash_type                    ; type of crash
      endm
 
BGL_TARGET_INDICATOR    macro x,y,z
      dw    0A6h
      dw    x,y,z
        endm
 
TEXTURED_ROAD_START     macro style,width,x,y,z
      dw    BGLOP_TEXTURED_ROAD     ; 0A8h
      dw    style
      dw    width
      dw    x,y,z
      endm
 
 
; OBJECT DATABASE ********************************************************
; Op    Format  Definition
; -----------------------------------------------------------------
; 14  db    14    ALWAYS LOAD HUGE OBJ ;00 opcode
;     dd    0     ;01 latitude iiii M units
;     dd    0     ;05 longitude 32-bit pseudo
;     db    0     ;09 image power
;     dd    0     ;10 byte count
;     db    0,0,0,0.... ;14 data (up to 2^32-13 bytes)
 
 
ALWAYS_LOAD_OBJECT_HEADER     macro latitude,longitude,object_end
      LOCAL opcode
opcode      db    14
      dd    latitude,longitude
      db    255               ;image power
      dd    object_end-opcode
      endm
 
BGL_ZBIAS   macro zbias_value
            dw    0ACh
            dw    zbias_value
            endm
 
BGL_LIGHT   macro ltype,x,y,z,intensity,li_atten,sq_atten,color,nx,ny,nz
      dw    BGLOP_LIGHT     ; 0ADh
      dw    ltype       ; light type
      real4   x,y,z           ; light offset
      dd      intensity       ; light intensity
      real4 li_atten    ; linear attenuation factor
      real4 sq_atten    ; squared attenuation factor
      dd      color           ; light color
      real4 nx,ny,nz    ; light direction
      endm
 
IFINF1      macro dest,v,low,high
      local start
start  label word
      dw        0B3h    ; BGLOP_IFINF1    ; 0B3h
      dd        (offset dest)-(offset start)
      dw        v
      real4 low
      real4 high
      endm
 
list_end_n = 0
 
BGL_BEGIN macro version
      dw    BGLOP_BEGIN
      dd    version
      endm
 
BGL_END macro
      dw    BGLOP_END
      endm
 
TEXTURE_SIZE macro f
      dw    BGLOP_TEXTURE_SIZE
      real4 f
      endm
 
TEXTURE_LIST_BEGIN      macro n,c
      dw    BGLOP_TEXTURE_LIST
      OFF_LABEL  list_end, %(list_end_n), 6, 64+4*4
      dd          0
      endm
 
TEXTURE_DEF macro tclass,color,f,name
      local name_start,name_end
      dd    tclass            ; texture class
      db    color       ; fallback color
      dd    0                 ; handle / hint
ifnb <f>
      real4 f           ; lod factor
else
      real4 0.0         ; lod factor
endif
name_start label byte
      db    name        ; name
name_end label byte
      db    (64 - ((offset name_end) - (offset name_start))) dup(0)
      endm
 
TEXTURE_LIST_END    macro n
      GEN_LABEL list_end, %(list_end_n), word
      list_end_n = list_end_n + 1
      endm
 
VERTEX_LIST_BEGIN  macro
      dw    BGLOP_VERTEX_LIST
      OFF_LABEL  list_end, %(list_end_n), 6, 8*4
      dd          0
      endm
 
VERTEX_DEF macro x,y,z,nx,ny,nz,tu,tv
      real4 x,y,z,nx,ny,nz,tu,tv
      endm
 
VERTEX_LIST_END macro
      GEN_LABEL list_end, %(list_end_n), word
      list_end_n = list_end_n + 1
      endm
 
MATERIAL_LIST_BEGIN  macro
      dw    BGLOP_MATERIAL_LIST
      OFF_LABEL  list_end, %(list_end_n), 6, 17*4
      dd          0
      endm
 
MATERIAL_DEF macro dr,dg,db,da, ar,ag,ab, sr,sg,sb, er,eg,eb, sp
      real4 dr,dg,db,da       ; diffuse
      real4 ar,ag,ab,1.0      ; ambient
      real4 sr,sg,sb,1.0      ; specular
      real4 er,eg,eb,1.0      ; emissive
      real4 sp                      ; specular power
      endm
 
MATERIAL_LIST_END macro
      GEN_LABEL list_end, %(list_end_n), word
      list_end_n = list_end_n + 1
      endm
 
MATERIAL macro iMat, iTex
      dw    BGLOP_SET_MATERIAL
      dw    iMat
ifnb <iTex>
      dw    iTex
else
      dw    -1
endif
      endm
 
 
DRAW_TRI_BEGIN    macro vertex_base, vertex_count
      dw    BGLOP_DRAW_TRILIST
      dw    vertex_base
      dw    vertex_count
      OFF_LABEL  list_end, %(list_end_n),2,2
      endm
 
DRAW_TRI macro    v0, v1, v2
      dw    v0, v1, v2
      endm
 
DRAW_TRI_END macro
      GEN_LABEL list_end, %(list_end_n), word
      list_end_n = list_end_n + 1
      endm
 
DRAW_LINE_BEGIN  macro vertex_base, vertex_count
      dw    BGLOP_DRAW_LINELIST
      dw    vertex_base
      dw    vertex_count
      OFF_LABEL list_end, %(list_end_n),2,2
      endm
 
DRAW_LINE macro v0, v1
      dw    v0, v1
      endm
 
DRAW_LINE_END macro
      GEN_LABEL list_end, %(list_end_n), word
      list_end_n = list_end_n + 1
      endm
 
DRAW_POINT_BEGIN  macro vertex_base, vertex_count
      dw    BGLOP_DRAW_POINTLIST
      dw    vertex_base
      dw    vertex_count
      OFF_LABEL list_end, %(list_end_n),2,2
      endm
 
DRAW_POINT macro v0
      dw    v0
      endm
 
DRAW_POINT_END macro
      GEN_LABEL list_end, %(list_end_n), word
      list_end_n = list_end_n + 1
      endm
 
TAXIWAY_SIGN_LIST_BEGIN  macro      lat,latf,lon,lonf,alt,altf,xofset,zofset,xbound,zbound
      dw    BGLOP_TAXIWAY_SIGN_LIST
      OFF_LABEL  list_end, %(list_end_n), 36, 1
      dw    latf
      dd    lat
      dw    lonf
      dd    lon
      dw    altf        ; dummy altitude to be filled in by
      dd    alt               ; command itself
      real4 xofset,zofset           ; meter units
      real4 xbound,zbound           ; meter units
      endm
 
sign_defn_n = 0
GEN_ALIGN macro name, n
      db    ($-(offset &name&_&n)) AND 1 dup (0)
endm
 
TAXIWAY_SIGN_DEF macro dx, dy, dz, dir, flags, _size, sign_label
 
      real4 dx, dy, dz        ; relative position     (meter units)
      real4 dir                     ; direction (radians, 0.0=East)
      db          flags
      db          _size
      GEN_LABEL sign_defn_n, %(sign_defn_n), word
      db    sign_label
      db    0
      GEN_ALIGN sign_defn_n, %(sign_defn_n)
      sign_defn_n = sign_defn_n + 1
      endm
 
TAXIWAY_SIGN_LIST_END macro
      GEN_LABEL list_end, %(list_end_n), word
      list_end_n = list_end_n + 1
      endm
 
MOUSERECT_LIST_BEGIN    macro n,c
      dw    BGLOP_MOUSERECT_LIST
      OFF_LABEL  list_end, %(list_end_n), 2, 11*4
      endm
 
MOUSE_CHILD_EVENT macro cursor, help_id, mouse_flags, event_id, tooltip_id, tooltip_metric_id, tooltip_english_id
      dd    2                 ; rect_type = MOUSE_RECT_CHILD
ifnb<tooltip_id>
      dd  tooltip_id    ; relative_box.x
else
      dd    0
endif
      dd    0                 ; relative_box.y
ifnb<tooltip_metric_id>
      dd  tooltip_metric_id   ; relative_box.size_x
else
      dd    0
endif
ifnb<tooltip_english_id>
      dd  tooltip_english_id  ; relative_box.size_y
else
      dd    0
endif
      dd    cursor            ; cursor
      dd    help_id           ; help_id
      dd    mouse_flags ; mouse_flags
      dd    event_id    ; event_id
      dd    0                 ; mouse_function
      dd    0                 ; api_data
      endm
 
MOUSE_CHILD_FUNCT macro cursor, help_id, mouse_flags, funct_id, tooltip_id, tooltip_metric_id, tooltip_english_id
      dd    2                 ; rect_type = MOUSE_RECT_CHILD
ifnb<tooltip_id>
      dd  tooltip_id    ; relative_box.x
else
      dd    0
endif
      dd    0                 ; relative_box.y
ifnb<tooltip_metric_id>
      dd  tooltip_metric_id   ; relative_box.size_x
else
      dd    0
endif
ifnb<tooltip_english_id>
      dd  tooltip_english_id  ; relative_box.size_y
else
      dd    0
endif
      dd    cursor            ; cursor
      dd    help_id           ; help_id
      dd    mouse_flags ; mouse_flags
      dd    0                 ; event_id
      dd    funct_id    ; mouse_function
      dd    0                 ; api_data
      endm
 
 
;MOUSE_TOOLTIP macro tooltip
;     local i
;     i = 0
;     FORC ch, <tooltip>
;           if i mod (9*4) eq 0
;                 dd  4                         ; rect_type = MOUSE_RECT_USER
;                 dd    MOUSERECT_TOOLTIP ; user_type
;           endif
;           db    '&ch&'
;           i = i + 1
;           endm
;     while i mod (9*4) ne 0
;           db    0
;           i = i + 1
;           endm
;     endm
MOUSE_TOOLTIP macro tooltip
      local name_start,name_end
      dd  4                         ; rect_type = MOUSE_RECT_USER
      dd    MOUSERECT_TOOLTIP ; user_type
name_start label byte
      db    tooltip           ; name
name_end label byte
      db    ((9*4) - ((offset name_end) - (offset name_start))) dup(0)
      endm
 
MOUSE_CALLBACK_STRING macro parmstring
      local name_start,name_end
      dd  4                         ; rect_type = MOUSE_RECT_USER
      dd    MOUSERECT_PARMS         ; user_type
name_start label byte
      db    parmstring              ; string
name_end label byte
      db    ((9*4) - ((offset name_end) - (offset name_start))) dup(0)
      endm
 
MOUSE_CALLBACK_LANGUAGE macro callbackcode
      MOUSE_CALLBACK_STRING   <callbackcode>
      endm
 
MOUSE_CALLBACK_DRAG macro setevent_id, varscale, varbias, xscale, yscale, minvalue, maxvalue
      local par_start,par_end
      dd  4                         ; rect_type = MOUSE_RECT_USER
      dd    MOUSERECT_PARMS         ; user_type
par_start label byte
      real4 varscale
      real4 varbias
      real4 xscale
      real4 yscale
ifnb<minvalue>
      dd          minvalue
else
      dd          80000000h
endif
ifnb<maxvalue>
      dd          maxvalue
else
      dd          7FFFFFFFh
endif
      dd          setevent_id
par_end label byte
      db    ((9*4) - ((offset par_end) - (offset par_start))) dup(0)
      endm
 
MOUSE_CALLBACK_DRAG_STEP macro xdelta, ydelta, inc_event_id, dec_event_id, inc_event_value, dec_event_value
      local par_start,par_end
      dd  4                         ; rect_type = MOUSE_RECT_USER
      dd    MOUSERECT_PARMS         ; user_type
par_start label byte
      dd          xdelta
      dd          ydelta
      dd          inc_event_id
ifnb<inc_event_value>
      dd          inc_event_value
else
      dd          0
endif
      dd          dec_event_id
ifnb<dec_event_value>
      dd          dec_event_value
else
      dd          0
endif
par_end label byte
      db    ((9*4) - ((offset par_end) - (offset par_start))) dup(0)
      endm
 
MOUSERECT_LIST_END    macro n
      dd    11 dup(0)   ; MOUSE_END
      GEN_LABEL list_end, %(list_end_n), word
      list_end_n = list_end_n + 1
      endm
 
SET_MOUSERECT     macro n
      dw    BGLOP_SET_MOUSERECT
      dw    n
      endm
 
END_MOUSERECT     macro
      dw    BGLOP_SET_MOUSERECT
      dw    -1
      endm
 
MATERIAL_ANIMATE macro iMat, iTex, nTex, input_base, input_ofs
      dw    BGLOP_SET_MATERIAL_ANIMATE      ; opcode = BGLOP_ANIMATE_INDIRECT = 0C1h
      dw    iMat
      dw    iTex
      dw    nTex
      dd    input_base              ; var_base_32 of input
      dd    input_ofs               ; variables offset to add to var_base
      endm
 
MODWORD macro input_base, input_ofs, output_base, output_ofs, mod_base, mod_ofs
      dw    BGLOP_MODWORD                   ; opcode = BGLOP_ANIMATE_INDIRECT = 0C2h
      dd    input_base              ; var_base_32 of input
      dd    input_ofs               ; variables offset to add to var_base
      dd    output_base             ; var_base_32 of output
      dd    output_ofs              ; variables offset to add to var_base
      dd    mod_base                ; var_base_32 of mod
      dd    mod_ofs                         ; variables offset to add to var_base
      endm
 
BGL_ANIMATE_INDIRECT    macro      input_base,input_ofs,table_base,table_ofs,xlate_x,xlate_y,xlate_z,matrix_index
      local start
start  label word
      dw    BGLOP_ANIMATE_INDIRECT        ; opcode = BGLOP_ANIMATE_INDIRECT = 0C3h
      dd    input_base              ; var_base_32 of input
      dd    input_ofs               ; variables offset to add to var_base
      dd    table_base              ; var_base_32 of table
      dd    table_ofs               ; variables offset to add to var_base
      real4 xlate_x,xlate_y,xlate_z       ; fixed translation
        dw      matrix_index                    ; index into the object matrix list to use
      endm
 
 
BGL_SET_MATRIX_INDIRECT macro matrix_index
      local start
start  label word
      dw    BGLOP_SET_MATRIX_INDIRECT     ; opcode = BGLOP_SET_MATRIX_INDIRECT = 0C4h
        dw      matrix_index                    ; index into the object matrix list to use
      endm
 
BGL_POINTVI_INDIRECT macro   dest,xx,yy,zz,pp,pv,bb,bv,hh,hv,matrix_index
      local do_jump, done, start
start  label word
      dw    BGLOP_POINTVI_INDIRECT
      dw    (offset do_jump)-(offset start)
      dw    xx,yy,zz
      dw    pp,pv,bb,bv,hh,hv
        dw      matrix_index
      ERRS16      (offset do_jump)-(offset start)
      JUMP  done
do_jump label word
      BGL_JUMP_32 dest
done  label word
      endm
 
BGL_TRANSFORM_INDIRECT  macro source_index, destination_index
      dw    BGLOP_TRANSFORM_INDIRECT      ; opcode = BGLOP_SET_MATRIX = 0C6h
        dw      source_index                    ; index into the transform matrix list for source matrix
        dw      destination_index               ; index into the animation matrix list for output matrix
        ERRS16  source_index
        ERRS16  destination_index
      endm
 
BGL_SCENEGRAPH_ENTRY   macro   output_matrix_index, child_node_index, peer_node_index, animation_command_size, animation_command_offset
        dw      output_matrix_index
        dw      child_node_index
        dw      peer_node_index
        dw      animation_command_size
        dd      animation_command_offset
        ERRS16  output_matrix_index
        ERRS16  child_node_index
        ERRS16  peer_node_index
        ERRS16  animation_command_size
        endm
 
BGL_ATTACHPOINT_ENTRY   macro   output_matrix_index, name_tag
        local   start
start   label   word
        dw      output_matrix_index
        dw      offset( name_tag ) - start
        ERRS16  output_matrix_index
        ERRS16  offset( name_tag ) - start
        endm
 
BGL_PLATFORM_ENTRY      macro   output_matrix_index, vertex_start_tag, vertex_count, surface_type
        local   start
start   label   word
        dw      output_matrix_index
        dw      offset( vertex_start_tag ) - start
        dw      vertex_count
        dw      surface_type
        ERRS16  output_matrix_index
        ERRS16  offset( vertex_start_tag ) - start
        ERRS16  vertex_count
        ERRS16  surface_type
        endm
 
BGL_PLATFORM_VERTEX_ENTRY       macro   vert_x, vert_y, vert_z
        real4   vert_x, vert_y, vert_z
        endm
 
 
; -----------------------------------------------------------------------------
; File:     bgl_header_macros.inc
;
; This file contains macros to generate the headers around objects and other
; data fragments that the frontend loads.
;
; -----------------------------------------------------------------------------
 
EOL   macro
      db    0
      endm
 
LATBAND_START macro
      rel_base = $
      endm
 
LATBAND_END macro
      db    0
      endm
 
LATBAND_REL macro latmin,latmax,band_addr
      db    21
      dw    latmin                  ; lat min (inclusive) 512M units
      dw    latmax                  ; lat max (exclusive)
      dd    band_addr-rel_base      ; 32-bit rel_base relative ptr
      endm
 
; -----------------------------------------------------------------------------
; -----------------------------------------------------------------------------
 
NEAR_SMALL_OBJECT_HEADER  macro   latitude,longitude,object_end,power
      LOCAL opcode
opcode      db    4
      dd    latitude,longitude
      ifnb <power>
      db    power             ; image power (0-100%)
      else
      db    100
      endif
      db    object_end-opcode
      endm
 
 
NEAR_LARGE_OBJECT_HEADER  macro   latitude,longitude,object_end,power
      LOCAL opcode
opcode      db    5
      dd    latitude,longitude
      ifnb <power>
      db    power             ; image power (0-100%)
      else
      db    100
      endif
      dw    object_end-opcode
      endm
 
LARGE_OBJECT_HEADER equ NEAR_LARGE_OBJECT_HEADER
 
NEAR_HUGE_OBJECT_HEADER   macro   latitude,longitude,object_end,power
      LOCAL opcode
opcode      db    6
      dd    latitude,longitude
      ifnb <power>
      db    power             ; image power (0-100%)
      else
      db    100
      endif
      dd    object_end-opcode
      endm
 
FAR_SMALL_OBJECT_HEADER       macro latitude,longitude,object_end,power
      LOCAL opcode
opcode      db    7
      dd    latitude,longitude
      ifnb <power>
      db    power             ; image power (0-100%)
      else
      db    100
      endif
      db    object_end-opcode
      endm
 
 
FAR_LARGE_OBJECT_HEADER macro latitude,longitude,object_end,power
      LOCAL opcode
opcode      db    8
      dd    latitude,longitude
      ifnb <power>
      db    power             ; image power (0-100%)
      else
      db    100
      endif
      dw    object_end-opcode
      endm
 
 
FAR_HUGE_OBJECT_HEADER  macro latitude,longitude,object_end,power
      LOCAL opcode
opcode      db    9
      dd    latitude,longitude
      ifnb <power>
      db    power             ; image power (0-100%)
      else
      db    100
      endif
      dd    object_end-opcode
      endm
 
 
NEAR_FAR_SMALL_OBJECT_HEADER  macro latitude,longitude,object_end,power
      LOCAL opcode
opcode      db    10
      dd    latitude,longitude
      ifnb <power>
      db    power             ; image power (0-100%)
      else
      db    100
      endif
      db    object_end-opcode
      endm
 
 
NEAR_FAR_LARGE_OBJECT_HEADER  macro latitude,longitude,object_end,power
      LOCAL opcode
opcode      db    11
      dd    latitude,longitude
      ifnb <power>
      db    power             ; image power (0-100%)
      else
      db    100
      endif
      dw    object_end-opcode
      endm
 
 
NEAR_FAR_HUGE_OBJECT_HEADER   macro latitude,longitude,object_end,power
      LOCAL opcode
opcode      db    12
      dd    latitude,longitude
      ifnb <power>
      db    power             ; image power (0-100%)
      else
      db    100
      endif
      dd    object_end-opcode
      endm
 
FS5_SIM_SB        EQU         00000004ah
FS5_SIM_WEIGHT          EQU         00000004ch
FS5_SIM_VEL_X_BODY_AXIS_EXP         EQU         000000050h
FS5_SIM_VEL_Y_BODY_AXIS_EXP         EQU         000000052h
FS5_SIM_VEL_Z_BODY_AXIS_EXP         EQU         000000054h
FS5_SIM_ACC_X_WORLD           EQU         000000056h
FS5_SIM_ACC_Z_WORLD           EQU         00000005eh
FS5_SIM_ACC_Z_BODY_AXIS32           EQU         000000070h
FS5_UNKNOWN_7A          EQU         00000007ah
FS5_AIRFRAME            EQU         00000007ch
FS5_CG_TO_GROUND_X            EQU         00000007eh
FS5_SIM_IZZ       EQU         000000090h
altmsl            EQU         000000280h
beacnt            EQU         000000282h
crash       EQU         000000284h
radflg            EQU         000000286h
rpfuel            EQU         000000288h
VERSION_IDENT           EQU         00000028ah
tod         EQU         00000028ch
logol_xv          EQU         00000029ch
logol_yv          EQU         00000029eh
logol_zv          EQU         0000002a0h
hv          EQU         0000002a6h
gndlevl           EQU         0000002eeh
gndlevlw1         EQU         0000002efh
gndlevlw2         EQU         0000002f0h
MAGVAR            EQU         0000002f4h
becon2            EQU         00000030ah
becon3            EQU         00000030ch
becon4            EQU         00000030eh
becon5            EQU         000000310h
usrvar            EQU         000000312h
usrvr2            EQU         000000314h
usrvr3            EQU         000000316h
usrvr4            EQU         000000318h
usrvr5            EQU         00000031ah
SHADOW_FLAG       EQU         000000338h
RBIAS       EQU         00000033ah
RBIAS1            EQU         00000033bh
RBIAS2            EQU         00000033ch
preferred_span          EQU         00000033eh
GROUND_TEXTURE          EQU         000000340h
BUILDING_TEXTURE        EQU         000000342h
AIRCRAFT_TEXTURE        EQU         000000344h
image_complex           EQU         000000346h
TEXTURE_AVAIL           EQU         000000348h
anti_alias        EQU         00000034ah
overflow          EQU         00000034eh
groundalt         EQU         000000350h
rootvar_free0           EQU         000000360h
hour        EQU         000000362h
minute            EQU         000000363h
image_complexity_cycl         EQU         000000364h
rootvar_free1           EQU         000000366h
rootvar_free2           EQU         000000368h
rootvar_free3           EQU         00000036ah
rootvar_free4           EQU         00000036ch
tp0         EQU         00000036eh
tp1         EQU         000000370h
tp2         EQU         000000372h
tp3         EQU         000000374h
tp4         EQU         000000376h
tp5         EQU         000000378h
OUT_OF_RANGE            EQU         00000037ah
xvlow       EQU         00000037ch
xv          EQU         00000037eh
yvlow       EQU         000000380h
yv          EQU         000000382h
zvlow       EQU         000000384h
zv          EQU         000000386h
BGL_ZULU_MINUTE         EQU         000000388h
BGL_ZULU_HOUR           EQU         000000389h
BGL_ZULU_DAY            EQU         00000038ah
BGL_ZULU_YEAR           EQU         00000038ch
TIME_ZONE_OFS           EQU         00000038eh
WATER_TEXTURE           EQU         000000390h
VISUAL_LAT_MIRROR       EQU         000000392h
VISUAL_LON_MIRROR       EQU         000000394h
VISUAL_ALT_MIRROR       EQU         000000396h
show_stars_bgl          EQU         0000003dch
BGL_TICK18        EQU         0000005fch
SEASON_CYCL       EQU         0000006f8h
color_var         EQU         000000734h
adf_freq          EQU         0000007bch
cmfreq            EQU         0000007beh
nvfreq            EQU         0000007c0h
pvfreq            EQU         0000007c2h
trans_freq        EQU         0000007c4h
adf_ext_freq            EQU         0000007c6h
ground            EQU         0000007d4h
BGL_ELAPSED_SECONDS           EQU         000000b40h
global_winds_surface_velocity       EQU         000000c72h
global_winds_surface_direction            EQU         000000c74h
global_winds_surface_turbulence           EQU         000000c76h
ENG1_STARTER            EQU         0000016beh
sky_type          EQU         0000019b4h
gradient_horiz          EQU         0000019bah
plane0lat         EQU         000001ba0h
plane0lon         EQU         000001ba6h
plane0alt         EQU         000001bach
plane0pitch       EQU         000001bb2h
plane0bank        EQU         000001bb6h
plane0heading           EQU         000001bbah
visual_lat        EQU         000001be8h
TEXTURE_QUALITY         EQU         000001ec8h
 
 
UINT16            TYPEDEF     WORD
UINT32            TYPEDEF     DWORD
SINT16            TYPEDEF           SWORD
SINT32            TYPEDEF     SDWORD
FLAGS16     TYPEDEF     WORD
FLAGS32     TYPEDEF     DWORD
BGLCODE           TYPEDEF           WORD
FLOAT32           TYPEDEF           REAL4
VAR32       TYPEDEF     DWORD
VAR16       TYPEDEF     WORD
ANGL16            TYPEDEF           VAR16
ANGL32            TYPEDEF     VAR32
ENUM16            TYPEDEF     VAR16
ENUM32            TYPEDEF     VAR32
 
GUID128     STRUCT 4t
id1         UINT32            ?
id2         UINT32            ?
id3         UINT32            ?
id4         UINT32            ?
GUID128     ENDS
 
;  LatLonAlt - used to store a position in 3D space
LATLONALT       STRUCT 4t
lat         QWORD       ?
lon         QWORD       ?
alt         QWORD       ?
LATLONALT       ENDS
 
;  PBH32 & PBH16 - rotation parameters of an object
PBH32       STRUCT 4t
pitch       DWORD       ?
bank        DWORD       ?
heading     DWORD       ?
PBH32       ENDS
 
PBH16       STRUCT 4t
pitch       ANGL16            ?
bank        ANGL16            ?
heading           ANGL16            ?
PBH16       ENDS
 
LLAPBH            STRUCT 4t
lla         LATLONALT         <>
pbh         PBH32       <>
LLAPBH            ENDS
 
XYZ16       STRUCT 4t
x           SINT16            ?
y           SINT16            ?
z           SINT16            ?
XYZ16       ENDS
 
FALSE       EQU         0
TRUE        EQU         1
 
BIT0        EQU         000000001h
BIT1        EQU         000000002h
BIT2        EQU         000000004h
BIT3        EQU         000000008h
BIT4        EQU         000000010h
BIT5        EQU         000000020h
BIT6        EQU         000000040h
BIT7        EQU         000000080h
BIT8        EQU         000000100h
BIT9        EQU         000000200h
BIT10       EQU         000000400h
BIT11       EQU         000000800h
BIT12       EQU         000001000h
BIT13       EQU         000002000h
BIT14       EQU         000004000h
BIT15       EQU         000008000h
BIT16       EQU         000010000h
 
GEN_MODEL_INSIDE        EQU         000000001h
GEN_MODEL_OUTSIDE       EQU         000000002h
GEN_MODEL_DOWNWARD            EQU         000000008h
GEN_MODEL_FRONT         EQU         000000010h
GEN_MODEL_REAR                EQU         000000020h
GEN_MODEL_ONGROUND            EQU         000002000h
GEN_MODEL_HARDWARE            EQU         000004000h
GEN_MODEL_DISPLAY       EQU         000008000h
GEN_MODEL_NOSHADOW            EQU         000001000h
 
LIGHT_NAV_MASK                EQU         000000001h
LIGHT_BEACON_MASK       EQU         000000002h
LIGHT_LANDING_MASK            EQU         000000004h
LIGHT_TAXI_MASK         EQU         000000008h
LIGHT_STROBE_MASK       EQU         000000010h
LIGHT_PANEL_MASK        EQU         000000020h
LIGHT_RECOGNITION_MASK        EQU         000000040h
LIGHT_WING_MASK         EQU         000000080h
LIGHT_LOGO_MASK         EQU         000000100h
 
LIGHT_BEACON                  EQU         0t
LIGHT_WING              EQU         1t
LIGHT_LOGO              EQU         2t
LIGHT_TAXI              EQU         3t
LIGHT_NAV               EQU         4t
LIGHT_LANDING                 EQU         5t
LIGHT_STROBE                  EQU         6t
LIGHT_RECOGNITION       EQU         7t
LIGHT_NONE              EQU         8t
LIGHT_LANDING_0         EQU         9t
LIGHT_TAXI_0                  EQU         10t
LIGHT_LANDING_1         EQU         11t
LIGHT_TAXI_1                  EQU         12t
 
AMBIENT_PRECIP_NONE           EQU         000000002h
AMBIENT_PRECIP_RAIN           EQU         000000004h
AMBIENT_PRECIP_SNOW           EQU         000000008h
AMBIENT_PRECIP_ANY            EQU         00000000ch
 
C_BLACK     EQU         00000f000h
C_WHITE     EQU         00000f004h
C_WATER           EQU         00000f00eh
G_DKGRAY    EQU         00000f001h
G_GRAY            EQU         00000f002h
G_LTGRAY    EQU         00000f003h
G_WHITE           EQU         00000f004h
G_RED       EQU         00000f005h
G_GREEN           EQU         00000f006h
G_BLUE            EQU         00000f007h
G_ORANGE    EQU         00000f008h
G_YELLOW    EQU         00000f009h
G_BROWN           EQU         00000f00ah
G_TAN       EQU         00000f00bh
G_BRICK           EQU         00000f00ch
G_OLIVE     EQU         00000f00dh
 
;  defines for aircraft model param:  parts_visible
VISIBLE_RIGHTWING EQU   000000001h
VISIBLE_LEFTWING  EQU   000000002h
VISIBLE_TAIL            EQU   000000004h
VISIBLE_ALLOTHER  EQU   000000008h
VISIBLE_AIRFRAME  EQU   00000000fh
VISIBLE_ENDCAP_LEFT     EQU   000000010h
VISIBLE_ENDCAP_RIGHT    EQU   000000020h
VISIBLE_ENDCAP_TAIL     EQU   000000040h
VISIBLE_PILOT           EQU   000000080h
VISIBLE_LEFTWINGTIP     EQU   000000100h
VISIBLE_RIGHTWINGTIP    EQU   000000200h
VISIBLE_NOSE            EQU   000000800h
VISIBLE_ENGINE0   EQU   000001000h
VISIBLE_ENGINE1   EQU   000002000h
VISIBLE_ENGINE2   EQU   000004000h
VISIBLE_ENGINE3   EQU   000008000h
 
; endcaps1
VISIBLE_ENDCAP0_LEFTWINGTIP   EQU   000000001h
VISIBLE_ENDCAP1_LEFTWINGTIP   EQU   000000002h
VISIBLE_ENDCAP2_LEFTWINGTIP   EQU   000000004h
VISIBLE_ENDCAP0_RIGHTWINGTIP  EQU   000000008h
VISIBLE_ENDCAP1_RIGHTWINGTIP  EQU   000000010h
VISIBLE_ENDCAP2_RIGHTWINGTIP  EQU   000000020h
VISIBLE_ENDCAP0_TAIL          EQU   000000040h
VISIBLE_ENDCAP1_TAIL          EQU   000000080h
VISIBLE_ENDCAP2_TAIL          EQU   000000100h
VISIBLE_ENDCAP0_NOSE          EQU   000000200h
VISIBLE_ENDCAP1_NOSE          EQU   000000400h
VISIBLE_ENDCAP2_NOSE          EQU   000000800h
VISIBLE_ENDCAP0_ENGINE0       EQU   000001000h
VISIBLE_ENDCAP1_ENGINE0       EQU   000002000h
VISIBLE_ENDCAP2_ENGINE0       EQU   000004000h
VISIBLE_ENDCAP0_ENGINE1       EQU   000008000h
 
; endcaps2
VISIBLE_ENDCAP1_ENGINE1       EQU   000000001h
VISIBLE_ENDCAP2_ENGINE1       EQU   000000002h
VISIBLE_ENDCAP0_ENGINE2       EQU   000000004h
VISIBLE_ENDCAP1_ENGINE2       EQU   000000008h
VISIBLE_ENDCAP2_ENGINE2       EQU   000000010h
VISIBLE_ENDCAP0_ENGINE3       EQU   000000020h
VISIBLE_ENDCAP1_ENGINE3       EQU   000000040h
VISIBLE_ENDCAP2_ENGINE3       EQU   000000080h
VISIBLE_ENDCAP0_LEFTWING      EQU   000000100h
VISIBLE_ENDCAP1_LEFTWING      EQU   000000200h
VISIBLE_ENDCAP2_LEFTWING      EQU   000000400h
VISIBLE_ENDCAP0_RIGHTWING     EQU   000000800h
VISIBLE_ENDCAP1_RIGHTWING     EQU   000001000h
VISIBLE_ENDCAP2_RIGHTWING     EQU   000002000h
 
; damaged0:
DAMAGE_LEFTHORIZONTAL         EQU   000000001h
DAMAGE_RIGHTHORIZONTAL        EQU   000000002h
DAMAGE_VERTICAL         EQU   000000004h
DAMAGE_RIGHTVERTICAL          EQU   000000008h
 
AIRCRAFT_PARAMS         STRUCT 4t
      params_length           UINT32            ?
      llapbh                  LLAPBH            <>
      visual_lla        LATLONALT   <>
      color_table       UINT16            16t DUP (?)
      texture           UINT16            ?
      texture_dir       DWORD       ?
      gen_model         FLAGS32     ?
      gear_smoke        UINT16            ?
      left_ailer        UINT16            ?
      right_ailer       UINT16            ?
      left_flap         UINT16            ?
      right_flap        UINT16            ?
      elevator          UINT16            ?
      rudder                  UINT16            ?
      engine_rpm        UINT16            ?
      prop_pos          UINT16            ?
      front_gear_p            UINT16            ?
      left_gear_p       UINT16            ?
      left_gear_b       UINT16            ?
      right_gear_p            UINT16            ?
      right_gear_b            UINT16            ?
      lights                  UINT16            ?
      strobe                  UINT16            ?
      prop_visible            UINT16            ?
      bomb_rocket_visible     FLAGS16     ?
      parts_visible           FLAGS16     ?
      scale             UINT32            ?
AIRCRAFT_PARAMS         ENDS
 
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;     include fs5_map.inc
SHADOW_FLAG             EQU             000000338h
image_complex           EQU             000000346h
becon2                  EQU             00000030ah
becon3                  EQU             00000030ch
becon4                  EQU             00000030eh
becon5                  EQU             000000310h
beacnt                  EQU             000000282h
usrvar                  EQU             000000312h
usrvr2                  EQU             000000314h
usrvr3                  EQU             000000316h
usrvr4                  EQU             000000318h
usrvr5                  EQU             00000031ah
BGL_TICK18              EQU             0000005fch
 
app_milliseconds_low    EQU             0000002403h
app_milliseconds_high   EQU             0000002404h
 
