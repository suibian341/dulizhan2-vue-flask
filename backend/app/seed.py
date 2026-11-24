from datetime import datetime, timedelta

from werkzeug.security import generate_password_hash

from .extensions import db
from .models import (
    Banner,
    BannerTranslation,
    Category,
    CategoryTranslation,
    Product,
    ProductImage,
    ProductTranslation,
    ProductVariant,
    Review,
    User,
)
from .spec_template_store import load_spec_template


LOCALES = ("en", "zh")
BANNER_LOCALES = ("en", "zh", "ja", "ko", "fr", "de", "es", "ar")

CATEGORIES = [
    {
        "slug": "eu-standard",
        "image": "/images/categories/01_欧规.png",
        "en": {"name": "EU Standard (Type C/F)", "description": "European standard plugs and adapters"},
        "zh": {"name": "欧规", "description": "欧洲标准插头及转换器"},
    },
    {
        "slug": "uk-standard",
        "image": "/images/categories/02_大英规.png",
        "en": {"name": "UK Standard (Type G)", "description": "British standard plugs and adapters"},
        "zh": {"name": "大英规", "description": "英国标准插头及转换器"},
    },
    {
        "slug": "uk-small-standard",
        "image": "/images/categories/03_小英规.png",
        "en": {"name": "Small UK Standard", "description": "Small British standard plugs and adapters"},
        "zh": {"name": "小英规", "description": "小英标插头及转换器"},
    },
    {
        "slug": "us-2pin",
        "image": "/images/categories/04_两脚美规.png",
        "en": {"name": "US 2-Pin (Type A)", "description": "American 2-pin plugs and adapters"},
        "zh": {"name": "两脚美规", "description": "美国两脚插头及转换器"},
    },
    {
        "slug": "us-3pin",
        "image": "/images/categories/05_三脚美规.png",
        "en": {"name": "US 3-Pin (Type B)", "description": "American 3-pin grounded plugs and adapters"},
        "zh": {"name": "三脚美规", "description": "美国三脚接地插头及转换器"},
    },
    {
        "slug": "au-standard",
        "image": "/images/categories/06_三脚澳规.png",
        "en": {"name": "AU Standard (Type I)", "description": "Australian standard plugs and adapters"},
        "zh": {"name": "三脚澳规", "description": "澳大利亚标准插头及转换器"},
    },
    {
        "slug": "thailand-standard",
        "image": "/images/categories/07_泰国规.png",
        "en": {"name": "Thailand Standard", "description": "Thai standard plugs and adapters"},
        "zh": {"name": "泰国规", "description": "泰国标准插头及转换器"},
    },
    {
        "slug": "brazil-standard",
        "image": "/images/categories/08_巴西规.png",
        "en": {"name": "Brazil Standard (Type N)", "description": "Brazilian standard plugs and adapters"},
        "zh": {"name": "巴西规", "description": "巴西标准插头及转换器"},
    },
    {
        "slug": "cn-2pin",
        "image": "/images/categories/09_国标中规两脚.png",
        "en": {"name": "China 2-Pin (Type A)", "description": "Chinese national standard 2-pin plugs"},
        "zh": {"name": "国标中规两脚", "description": "中国国标两脚插头及转换器"},
    },
    {
        "slug": "cn-3pin",
        "image": "/images/categories/10_国标中规三脚.png",
        "en": {"name": "China 3-Pin (Type I)", "description": "Chinese national standard 3-pin plugs"},
        "zh": {"name": "国标中规三脚", "description": "中国国标三脚插头及转换器"},
    },
    {
        "slug": "india-standard",
        "image": "/images/categories/11_印度规.png",
        "en": {"name": "India Standard (Type D/M)", "description": "Indian standard plugs and adapters"},
        "zh": {"name": "印度规", "description": "印度标准插头及转换器"},
    },
    {
        "slug": "argentina-standard",
        "image": "/images/categories/12_阿根廷规.png",
        "en": {"name": "Argentina Standard (Type I)", "description": "Argentine standard plugs and adapters"},
        "zh": {"name": "阿根廷规", "description": "阿根廷标准插头及转换器"},
    },
]

PRODUCT_IMAGES = [
    "/images/products/product-1.png",
    "/images/products/product-2.png",
    "/images/products/product-3.png",
    "/images/products/product-4.png",
    "/images/products/product-5.png",
    "/images/products/product-6.png",
]

PRODUCT_TEMPLATES = [
    {
        "suffix": "smart-power-strip",
        "price": 299,
        "compare": 399,
        "en": {
            "name": "Smart Power Strip",
            "description": "WiFi-enabled smart power strip with app control, energy monitoring, and voice assistant compatibility.",
            "short": "WiFi control, energy monitoring",
        },
        "zh": {
            "name": "智能排插",
            "description": "支持WiFi连接的智能排插，APP远程控制、能耗监测、语音助手兼容。",
            "short": "WiFi控制，能耗监测",
        },
    },
    {
        "suffix": "gan-charger-station",
        "price": 399,
        "compare": 499,
        "en": {
            "name": "GaN Charging Station",
            "description": "100W GaN fast charging station with USB-C PD and multi-port output. 40% smaller than traditional chargers.",
            "short": "100W GaN, multi-port",
        },
        "zh": {
            "name": "GaN快充站",
            "description": "100W氮化镓快充站，USB-C PD多口输出，体积比传统方案缩小40%。",
            "short": "100W GaN，多口输出",
        },
    },
    {
        "suffix": "surge-protector",
        "price": 259,
        "compare": 329,
        "en": {
            "name": "Surge Protector Strip",
            "description": "4000V surge protection with 8 outlets and 4 USB ports. V-0 flame-retardant housing for maximum safety.",
            "short": "4000V protection, flame-retardant",
        },
        "zh": {
            "name": "浪涌保护排插",
            "description": "4000V浪涌防护，8个AC插孔+4个USB接口，V-0级阻燃外壳确保安全。",
            "short": "4000V防护，阻燃外壳",
        },
    },
    {
        "suffix": "travel-adapter",
        "price": 189,
        "compare": 249,
        "en": {
            "name": "Travel Adapter",
            "description": "Ultra-slim universal travel adapter with 3 AC outlets and 3 USB ports. TSA approved for carry-on.",
            "short": "Ultra-slim, universal",
        },
        "zh": {
            "name": "旅行转换器",
            "description": "超薄万能旅行转换器，3个AC插孔+3个USB接口，TSA认证可随身携带。",
            "short": "超薄设计，万能转换",
        },
    },
    {
        "suffix": "desktop-power-hub",
        "price": 349,
        "compare": 429,
        "en": {
            "name": "Desktop Power Hub",
            "description": "Under-desk mount power hub with cable management. 6 AC outlets + 2 USB-C PD ports for clean workspace.",
            "short": "Under-desk, cable management",
        },
        "zh": {
            "name": "桌面电源集线器",
            "description": "桌下安装式电源集线器，内置理线系统。6个AC插孔+2个USB-C PD接口。",
            "short": "桌下安装，理线管理",
        },
    },
    {
        "suffix": "wireless-charging-strip",
        "price": 329,
        "compare": 399,
        "en": {
            "name": "Wireless Charging Strip",
            "description": "Built-in 15W Qi wireless charging pad with 4 AC outlets and 3 USB ports. Modern minimalist design.",
            "short": "15W wireless, Qi-certified",
        },
        "zh": {
            "name": "无线充电排插",
            "description": "内置15W Qi无线充电板，4个AC插孔+3个USB接口，现代简约设计。",
            "short": "15W无线充电，Qi认证",
        },
    },
]

POWER_STRIP_SPEC_ROWS = [
    ("Basic Information", "基础信息", "Model No.", "产品型号", "203MS", "203MS"),
    ("Basic Information", "基础信息", "Product Name", "产品名称", "Power Strip / Extension Socket", "排插 / 插线板 / 延长插座"),
    ("Basic Information", "基础信息", "English Name", "英文名称", "Power Strip / Extension Socket", "Power Strip / Extension Socket"),
    ("Basic Information", "基础信息", "Product Type", "产品类型", "Multi-Outlet Power Strip", "多位电源排插"),
    ("Basic Information", "基础信息", "Country of Origin", "产地", "China", "中国"),
    ("Basic Information", "基础信息", "Brand", "品牌", "Own Brand / OEM / Neutral Brand, to be confirmed", "自有品牌 / OEM / 中性品牌，待确认"),
    ("Electrical Ratings", "电气参数", "Rated Voltage", "额定电压", "AC 220V-250V", "AC 220V-250V"),
    ("Electrical Ratings", "电气参数", "Rated Current", "额定电流", "10A", "10A"),
    ("Electrical Ratings", "电气参数", "Maximum Power", "最大功率", "2500W", "2500W"),
    ("Electrical Ratings", "电气参数", "Rated Frequency", "额定频率", "To be provided", "待补充"),
    ("Electrical Ratings", "电气参数", "Grounding Type", "接地方式", "To be provided", "待补充"),
    ("Materials & Construction", "材料结构", "Housing Material", "外壳材质", "Flame-Retardant PP", "阻燃PP"),
    ("Materials & Construction", "材料结构", "Conductive Parts", "导电件材质", "Full Copper", "全铜"),
    ("Materials & Construction", "材料结构", "Main Construction", "整体材料", "Flame-Retardant PP Housing + Full-Copper Conductive Parts", "阻燃PP外壳 + 全铜导电件"),
    ("Materials & Construction", "材料结构", "Flame-Retardant Rating", "阻燃等级", "To be provided", "待补充"),
    ("Safety Features", "安全功能", "Power Switch", "总控开关", "Included", "支持"),
    ("Safety Features", "安全功能", "Child Safety Shutters", "儿童安全保护门", "Included", "支持"),
    ("Safety Features", "安全功能", "Overload Protector", "过载保护器", "Included", "支持"),
    ("Safety Features", "安全功能", "Surge Protection", "浪涌保护器", "Optional", "可选"),
    ("Safety Features", "安全功能", "Fuse Protection", "保险丝保护", "13A fuse for UK plug configuration; other plugs to be confirmed", "英式插头配置13A保险丝；其他插头待确认"),
    ("Plug & Socket", "插头插座规格", "Plug Options", "插头类型", "13A UK Fused Plug, EU Plug, India Plug and other customized options", "13A英式保险丝插头、欧式插头、印度插头等，可定制"),
    ("Plug & Socket", "插头插座规格", "Number of Outlets", "插座位数", "2 / 3 / 4 / 5 / 6 Outlets", "2 / 3 / 4 / 5 / 6位"),
    ("Plug & Socket", "插头插座规格", "Socket Standard", "插座类型", "To be provided; configurable for the target market", "待补充，可按目标市场确认"),
    ("Plug & Socket", "插头插座规格", "Cable Length", "线长", "To be provided; customizable", "待补充，可定制"),
    ("Plug & Socket", "插头插座规格", "Cable Specification", "线材规格", "To be provided, e.g. 3G0.75mm² / 3G1.0mm²", "待补充，例如3G0.75mm² / 3G1.0mm²"),
    ("Plug & Socket", "插头插座规格", "Cable Material", "电源线材质", "To be provided", "待补充"),
    ("Plug & Socket", "插头插座规格", "Plug and Cable Color", "插头及电线颜色", "To be provided; customizable", "待补充，可定制"),
    ("Packaging & Logistics", "包装物流", "Unit Weight", "单个重量", "To be provided", "待补充"),
    ("Packaging & Logistics", "包装物流", "Unit Volume", "单个体积", "To be provided", "待补充"),
    ("Packaging & Logistics", "包装物流", "Product Dimensions", "产品尺寸", "To be provided", "待补充"),
    ("Packaging & Logistics", "包装物流", "Packaging Method", "包装方式", "To be provided, e.g. color box, white box, neutral box or OPP bag", "待补充，例如彩盒、白盒、中性盒、OPP袋"),
    ("Packaging & Logistics", "包装物流", "Individual Package Size", "单个包装尺寸", "To be provided", "待补充"),
    ("Packaging & Logistics", "包装物流", "Quantity per Carton", "外箱装量", "To be provided", "待补充"),
    ("Packaging & Logistics", "包装物流", "Carton Dimensions", "外箱尺寸", "To be provided", "待补充"),
    ("Packaging & Logistics", "包装物流", "Carton Gross / Net Weight", "外箱毛重 / 净重", "To be provided", "待补充"),
    ("Packaging & Logistics", "包装物流", "Customs Declaration", "海关敏感属性", "Electrical product with plug; no battery, liquid or dangerous goods. Subject to final customs documents", "电器类产品，带插头；不含电池、液体及危险品，具体以报关资料为准"),
    ("Packaging & Logistics", "包装物流", "HS Code", "HS编码", "To be provided", "待补充"),
    ("Certifications", "认证信息", "Available Certifications", "可提供认证", "To be provided, e.g. CE, RoHS, UKCA, BS1363, GCC, SASO or SONCAP", "待补充，例如CE、RoHS、UKCA、BS1363、GCC、SASO、SONCAP等"),
    ("Certifications", "认证信息", "Market Compliance", "认证适用说明", "Subject to plug type, product configuration and destination-market requirements", "按插头规格、产品配置及目标市场确认"),
    ("Certifications", "认证信息", "Test Reports", "测试报告", "To be provided", "待补充"),
    ("Backend Information", "后台商品信息", "Product Code", "商品编码", "To be provided", "待补充"),
    ("Backend Information", "后台商品信息", "SKU", "SKU", "Recommended format: Model-Outlets/Plug-Cable Length-Color-Function", "建议按“型号-位数及插头-线长-颜色-功能”生成"),
    ("Backend Information", "后台商品信息", "Product Barcode", "商品条码", "To be provided", "待补充"),
    ("Backend Information", "后台商品信息", "Barcode Type", "条码类型", "To be provided", "待补充"),
    ("Backend Information", "后台商品信息", "Product Status", "产品状态", "To be provided", "待补充"),
    ("Backend Information", "后台商品信息", "Inventory Status", "库存状态", "To be provided", "待补充"),
    ("Backend Information", "后台商品信息", "SEO Keywords", "SEO关键词", "Power Strip, Extension Socket, Multi Socket, Electrical Extension Board", "Power Strip、Extension Socket、Multi Socket、Electrical Extension Board"),
]

SPEC_OPTIONS = {
    "Rated Frequency": [("50/60Hz", "50/60Hz"), ("To be provided", "待补充")],
    "Grounding Type": [("Grounded / Earthed", "接地"), ("Ungrounded", "不接地"), ("To be provided", "待补充")],
    "Flame-Retardant Rating": [("V-0", "V-0"), ("V-1", "V-1"), ("V-2", "V-2"), ("To be provided", "待补充")],
    "Power Switch": [("Included", "支持"), ("Optional", "可选"), ("Not included", "不支持")],
    "Child Safety Shutters": [("Included", "支持"), ("Optional", "可选"), ("Not included", "不支持")],
    "Overload Protector": [("Included", "支持"), ("Optional", "可选"), ("Not included", "不支持")],
    "Surge Protection": [("Included", "支持"), ("Optional", "可选"), ("Not included", "不支持")],
    "Plug Options": [
        ("13A UK Fused Plug", "13A英式保险丝插头"),
        ("EU Plug", "欧式插头"),
        ("India Plug", "印度插头"),
        ("US Plug", "美式插头"),
        ("AU Plug", "澳规插头"),
        ("Customized Plug", "定制插头"),
    ],
    "Number of Outlets": [
        ("2 Outlets", "2位"),
        ("3 Outlets", "3位"),
        ("4 Outlets", "4位"),
        ("5 Outlets", "5位"),
        ("6 Outlets", "6位"),
        ("2 / 3 / 4 / 5 / 6 Outlets", "2 / 3 / 4 / 5 / 6位"),
    ],
    "Cable Length": [("1m", "1m"), ("1.5m", "1.5m"), ("2m", "2m"), ("3m", "3m"), ("To be provided; customizable", "待补充，可定制")],
    "Cable Specification": [("3G0.75mm²", "3G0.75mm²"), ("3G1.0mm²", "3G1.0mm²"), ("3G1.25mm²", "3G1.25mm²"), ("To be provided", "待补充")],
    "Packaging Method": [("Color box", "彩盒"), ("White box", "白盒"), ("Neutral box", "中性盒"), ("OPP bag", "OPP袋"), ("Customized packaging", "定制包装")],
    "Available Certifications": [("CE", "CE"), ("RoHS", "RoHS"), ("UKCA", "UKCA"), ("BS1363", "BS1363"), ("GCC", "GCC"), ("SASO", "SASO"), ("SONCAP", "SONCAP"), ("To be provided", "待补充")],
}

COMMON_SPEC_OPTIONS = [
    ("To be provided", "待补充"),
    ("To be confirmed", "待确认"),
    ("Included", "支持"),
    ("Optional", "可选"),
    ("Customizable", "可定制"),
    ("Not included", "不支持"),
]

BANNERS = [
    {
        "image": "/images/hero-banner.png",
        "sort": 0,
        "translations": {
            "en": (
                "Power Every Corner",
                "Smart strips with USB-C fast charging, remote control, and robust protection for modern homes and offices.",
                "Shop Now",
            ),
            "zh": (
                "全屋供电，一次到位",
                "智能排插、USB-C 快充、独立分控与远程联动，让家庭与办公桌面更整洁、更高效。",
                "立即选购",
            ),
        },
    },
    {
        "image": "/images/banner-1.png",
        "sort": 1,
        "translations": {
            "en": (
                "Universal Travel Companion",
                "One adapter for 200+ countries. Compact GaN design with multi-port fast charging keeps all your devices powered wherever you go.",
                "Explore Now",
            ),
            "zh": (
                "全球通用，一插走天下",
                "一个转换器覆盖 200+ 国家，GaN 紧凑设计搭配多口快充，出行再也不用担心充电问题。",
                "立即探索",
            ),
        },
    },
    {
        "image": "/images/banner-2.png",
        "sort": 2,
        "translations": {
            "en": (
                "Fast Charging, Built Safe",
                "GaN technology delivers high-speed charging with stable output and layered electrical safety for all your devices.",
                "View Solutions",
            ),
            "zh": (
                "快充与安全，不再二选一",
                "GaN 高效快充搭配多重防护设计，为手机、平板、笔记本和小家电提供稳定电力支持。",
                "查看方案",
            ),
        },
    },
    {
        "image": "/images/banner-3.png",
        "sort": 3,
        "translations": {
            "en": (
                "Desktop Power Hub",
                "Organize your workspace with multi-outlet power strips featuring individual switches, USB-C PD ports, and surge protection.",
                "Shop Desktop",
            ),
            "zh": (
                "桌面电力中枢",
                "多孔位独立开关排插，配备 USB-C PD 快充与浪涌保护，让桌面供电井然有序。",
                "选购桌面系列",
            ),
        },
    },
    {
        "image": "/images/banner-4.png",
        "sort": 4,
        "translations": {
            "en": (
                "Professional Protection",
                "Surge defense, overload protection, and flame-retardant housing to safeguard your valuable devices around the clock.",
                "Learn More",
            ),
            "zh": (
                "专业级用电保护",
                "从浪涌防护到过载保护，从阻燃外壳到精密结构，为关键设备提供持续稳定的电力保障。",
                "了解更多",
            ),
        },
    },
]

BANNER_TRANSLATION_OVERRIDES = [
    {
        "zh": ("全屋供电，一次到位", "智能排插、USB-C 快充、独立分控与远程联动，让家庭与办公桌面更整洁、更高效。", "立即选购"),
        "ja": ("家じゅうの電源を一括管理", "USB-C急速充電、個別スイッチ、リモート操作に対応したスマート電源タップで、家庭やオフィスをすっきり効率化。", "今すぐ購入"),
        "ko": ("집 안 전원을 한 번에 관리", "USB-C 고속 충전, 개별 스위치, 원격 제어를 갖춘 스마트 멀티탭으로 집과 사무실을 더 깔끔하고 효율적으로 만드세요.", "지금 쇼핑하기"),
        "fr": ("Alimentez chaque espace", "Multiprises intelligentes avec charge rapide USB-C, commandes individuelles et contrôle à distance pour la maison et le bureau.", "Acheter maintenant"),
        "de": ("Strom für jeden Bereich", "Smarte Steckdosenleisten mit USB-C-Schnellladen, Einzelschaltern und Fernsteuerung für Zuhause und Büro.", "Jetzt kaufen"),
        "es": ("Energía para cada rincón", "Regletas inteligentes con carga rápida USB-C, controles independientes y conexión remota para hogar y oficina.", "Comprar ahora"),
        "ar": ("طاقة لكل زاوية", "مشتركات ذكية مع شحن USB-C سريع، تحكم مستقل واتصال عن بعد لمنزل ومكتب أكثر تنظيما وكفاءة.", "تسوق الآن"),
    },
    {
        "zh": ("全球通用，一插走天下", "一个转换器覆盖 200+ 国家，GaN 紧凑设计搭配多口快充，出行不再担心充电问题。", "立即探索"),
        "ja": ("世界を旅する電源パートナー", "200以上の国と地域に対応。小型GaN設計と複数ポート急速充電で、どこでもデバイスをしっかり充電。", "詳しく見る"),
        "ko": ("전 세계 여행을 위한 전원 파트너", "200개 이상 국가를 지원하는 어댑터. 컴팩트한 GaN 설계와 멀티포트 고속 충전으로 어디서나 전원을 확보하세요.", "자세히 보기"),
        "fr": ("Votre compagnon de voyage universel", "Un adaptateur pour plus de 200 pays, avec conception GaN compacte et charge rapide multiport pour tous vos appareils.", "Explorer"),
        "de": ("Universeller Reisebegleiter", "Ein Adapter für über 200 Länder. Kompaktes GaN-Design und Multiport-Schnellladen für alle Geräte unterwegs.", "Entdecken"),
        "es": ("Compañero universal de viaje", "Un adaptador para más de 200 países. Diseño GaN compacto con carga rápida multipuerto para todos tus dispositivos.", "Explorar"),
        "ar": ("رفيق السفر العالمي", "محول واحد لأكثر من 200 دولة، بتصميم GaN مدمج وشحن سريع متعدد المنافذ لكل أجهزتك.", "استكشف الآن"),
    },
    {
        "zh": ("快充与安全，不再二选一", "GaN 高效快充搭配多重防护设计，为手机、平板、笔记本和小家电提供稳定电力支持。", "查看方案"),
        "ja": ("急速充電も安全性も妥協しない", "GaN技術による高速充電と多層保護で、スマートフォン、タブレット、ノートPC、小型家電まで安定給電。", "ソリューションを見る"),
        "ko": ("빠른 충전과 안전을 동시에", "GaN 고효율 고속 충전과 다중 전기 보호 설계로 휴대폰, 태블릿, 노트북, 소형 가전을 안정적으로 지원합니다.", "솔루션 보기"),
        "fr": ("Charge rapide, sécurité intégrée", "La technologie GaN offre une charge rapide et stable avec plusieurs protections électriques pour tous vos appareils.", "Voir les solutions"),
        "de": ("Schnellladen mit integrierter Sicherheit", "GaN-Technologie liefert schnelles, stabiles Laden mit mehrstufigem Schutz für Smartphone, Tablet, Laptop und Kleingeräte.", "Lösungen ansehen"),
        "es": ("Carga rápida con seguridad integrada", "La tecnología GaN ofrece carga de alta velocidad, salida estable y protección eléctrica por capas para todos tus dispositivos.", "Ver soluciones"),
        "ar": ("شحن سريع بأمان مدمج", "تقنية GaN توفر شحنا سريعا ومستقرا مع طبقات حماية كهربائية لكل أجهزتك.", "عرض الحلول"),
    },
    {
        "zh": ("桌面电力中枢", "多孔位独立开关排插，配备 USB-C PD 快充与浪涌保护，让桌面供电井然有序。", "选购桌面系列"),
        "ja": ("デスク周りの電源ハブ", "個別スイッチ付きの多口電源タップ、USB-C PD急速充電、サージ保護で作業スペースをすっきり整理。", "デスク向けを見る"),
        "ko": ("데스크 전원 허브", "개별 스위치 멀티 콘센트, USB-C PD 고속 충전, 서지 보호로 업무 공간의 전원을 깔끔하게 정리하세요.", "데스크 제품 보기"),
        "fr": ("Hub d'alimentation de bureau", "Organisez votre espace avec prises multiples, interrupteurs individuels, ports USB-C PD et protection contre les surtensions.", "Voir la gamme bureau"),
        "de": ("Desktop-Stromzentrale", "Mehrfachsteckdosen mit Einzelschaltern, USB-C PD und Überspannungsschutz bringen Ordnung auf den Schreibtisch.", "Desktop-Serie ansehen"),
        "es": ("Centro de energía para escritorio", "Ordena tu espacio con regletas de múltiples tomas, interruptores individuales, USB-C PD y protección contra sobretensiones.", "Ver escritorio"),
        "ar": ("مركز طاقة للمكتب", "نظم مساحة العمل بمشتركات متعددة المخارج مع مفاتيح مستقلة، USB-C PD وحماية من زيادة التيار.", "تسوق سلسلة المكتب"),
    },
    {
        "zh": ("专业级用电保护", "从浪涌防护到过载保护，从阻燃外壳到精密结构，为关键设备提供持续稳定的电力保障。", "了解更多"),
        "ja": ("プロ仕様の電源保護", "サージ防止、過負荷保護、難燃性ケースで、大切な機器を24時間しっかり守ります。", "詳しく知る"),
        "ko": ("전문가급 전원 보호", "서지 방어, 과부하 보호, 난연 하우징으로 중요한 장비를 24시간 안정적으로 보호합니다.", "더 알아보기"),
        "fr": ("Protection électrique professionnelle", "Protection contre les surtensions, surcharge et boîtier ignifuge pour sécuriser vos appareils essentiels en continu.", "En savoir plus"),
        "de": ("Professioneller Schutz", "Überspannungsschutz, Überlastschutz und flammhemmendes Gehäuse sichern wertvolle Geräte rund um die Uhr.", "Mehr erfahren"),
        "es": ("Protección eléctrica profesional", "Defensa contra sobretensiones, protección contra sobrecarga y carcasa ignífuga para proteger tus equipos críticos.", "Más información"),
        "ar": ("حماية طاقة احترافية", "حماية من الاندفاع والتحميل الزائد وهيكل مقاوم للاشتعال لحماية أجهزتك المهمة على مدار الساعة.", "اعرف المزيد"),
    },
]

for banner, translations in zip(BANNERS, BANNER_TRANSLATION_OVERRIDES):
    banner["translations"].update(translations)


def localized_text(en_value, zh_value):
    return {"en": en_value, "zh": zh_value}


def default_power_strip_specs():
    return load_spec_template()


def banner_texts(item, locale):
    translations = item.get("translations") or {}
    return translations.get(locale) or translations.get("en") or ("", "", "")


def ensure_default_banner_translations():
    default_by_image = {item["image"]: item for item in BANNERS}
    default_by_sort = {item["sort"]: item for item in BANNERS}
    changed = False
    for banner in Banner.query.filter_by(position="hero").all():
        item = default_by_image.get(banner.image) or default_by_sort.get(banner.sort_order)
        if not item:
            continue
        existing = {translation.locale: translation for translation in banner.translations}
        for locale in BANNER_LOCALES:
            title, subtitle, button_text = banner_texts(item, locale)
            if locale in existing:
                translation = existing[locale]
                if not translation.title or translation.title != title:
                    translation.title = title
                    changed = True
                if not translation.subtitle or translation.subtitle != subtitle:
                    translation.subtitle = subtitle
                    changed = True
                if not translation.button_text or translation.button_text != button_text:
                    translation.button_text = button_text
                    changed = True
                continue
            banner.translations.append(
                BannerTranslation(
                    locale=locale,
                    title=title,
                    subtitle=subtitle,
                    button_text=button_text,
                )
            )
            changed = True
    return changed


def ensure_root_admin():
    admin = User.query.filter_by(email="baomiai@126.com").first()
    if not admin:
        admin = User(email="baomiai@126.com")
        db.session.add(admin)
    admin.name = "baomiai"
    admin.role = "SUPER_ADMIN"
    admin.is_active = True
    admin.password_hash = generate_password_hash("baomiai99999")

    senior = User.query.filter_by(email="misicheng@001.com").first()
    legacy_senior = User.query.filter_by(email="misicheng01").first()
    if legacy_senior and not senior:
        legacy_senior.email = "misicheng@001.com"
        senior = legacy_senior
    elif legacy_senior and senior and legacy_senior.id != senior.id:
        db.session.delete(legacy_senior)
    if not senior:
        senior = User(email="misicheng@001.com")
        db.session.add(senior)
    senior.name = "misicheng01"
    senior.role = "SENIOR_ADMIN"
    senior.is_active = True
    senior.password_hash = generate_password_hash("misicheng01")

    legacy = User.query.filter_by(email="admin@misicheng.local").first()
    if legacy:
        legacy.name = "Misicheng Admin"
        legacy.role = "ADMIN"
        legacy.is_active = True


def trade_info_for(price, compare_price, category, template_index):
    compare_ratio = (compare_price / price) if price else 0

    def compare_for(value):
        return round(value * compare_ratio, 2) if compare_ratio else None

    return {
        "priceTiers": [
            {"minQty": 10, "maxQty": 99, "price": round(price, 2), "compareAtPrice": compare_for(price)},
            {"minQty": 100, "maxQty": 499, "price": round(price * 0.92, 2), "compareAtPrice": compare_for(price * 0.92)},
            {"minQty": 500, "maxQty": None, "price": round(price * 0.85, 2), "compareAtPrice": compare_for(price * 0.85)},
        ],
        "shipFrom": {"en": "Shenzhen / Yiwu", "zh": "深圳 / 义乌"},
        "plugStandard": {"en": category["en"]["name"], "zh": category["zh"]["name"]},
    }


def seed_database(force=False):
    if not force and Category.query.first():
        ensure_root_admin()
        ensure_default_banner_translations()
        db.session.commit()
        return

    db.session.query(Review).delete()
    db.session.query(ProductVariant).delete()
    db.session.query(ProductImage).delete()
    db.session.query(ProductTranslation).delete()
    db.session.query(Product).delete()
    db.session.query(CategoryTranslation).delete()
    db.session.query(Category).delete()
    db.session.query(BannerTranslation).delete()
    db.session.query(Banner).delete()
    ensure_root_admin()

    categories = []
    for index, item in enumerate(CATEGORIES):
        category = Category(
            slug=item["slug"],
            image=item["image"],
            sort_order=index,
            is_active=True,
        )
        category.translations = [
            CategoryTranslation(
                locale=locale,
                name=item[locale]["name"],
                description=item[locale]["description"],
                meta_title=item[locale]["name"],
                meta_description=item[locale]["description"],
            )
            for locale in LOCALES
        ]
        db.session.add(category)
        categories.append((category, item))

    db.session.flush()

    product_index = 0
    for category, category_data in categories:
        for template_index, template in enumerate(PRODUCT_TEMPLATES):
            price = template["price"]
            sku = f"PWR-{product_index + 1:03d}"
            image_index = product_index % len(PRODUCT_IMAGES)
            product_name_en = f"{category_data['en']['name']} {template['en']['name']}"
            product_name_zh = f"{category_data['zh']['name']}{template['zh']['name']}"
            product = Product(
                slug=f"{category_data['slug']}-{template['suffix']}",
                sku=sku,
                status="ACTIVE",
                is_featured=template_index == 0,
                is_new=template_index == 1,
                price=price,
                compare_at_price=template["compare"],
                category_id=category.id,
                brand_name="Misicheng",
                specifications=default_power_strip_specs(),
                trade_info=trade_info_for(price, template["compare"], category_data, template_index),
                sort_order=product_index,
            )
            product.translations = [
                ProductTranslation(
                    locale="en",
                    name=product_name_en,
                    description=template["en"]["description"],
                    short_description=template["en"]["short"],
                    meta_title=product_name_en,
                    meta_description=template["en"]["short"],
                ),
                ProductTranslation(
                    locale="zh",
                    name=product_name_zh,
                    description=template["zh"]["description"],
                    short_description=template["zh"]["short"],
                    meta_title=product_name_zh,
                    meta_description=template["zh"]["short"],
                ),
            ]
            product.images = [
                ProductImage(url=PRODUCT_IMAGES[image_index], alt=product_name_en, sort_order=0),
                ProductImage(
                    url=PRODUCT_IMAGES[(image_index + 1) % len(PRODUCT_IMAGES)],
                    alt=f"{product_name_en} detail",
                    sort_order=1,
                ),
            ]
            product.variants = [
                ProductVariant(
                    sku=f"{sku}-WH",
                    price=price,
                    compare_at_price=template["compare"],
                    stock=100,
                    options={"color": "White", "plug": category_data["en"]["name"]},
                    sort_order=0,
                ),
                ProductVariant(
                    sku=f"{sku}-BK",
                    price=price,
                    compare_at_price=template["compare"],
                    stock=80,
                    options={"color": "Black", "plug": category_data["en"]["name"]},
                    sort_order=1,
                ),
            ]
            product.reviews = [
                Review(
                    user_name="Procurement Lead",
                    rating=5,
                    title="Reliable sample quality",
                    comment="The product finish, packaging options, and safety details are clear for quotation.",
                    is_verified=True,
                ),
                Review(
                    user_name="Distribution Buyer",
                    rating=4,
                    title="Good for market matching",
                    comment="The plug standard and product family are easy to match with regional demand.",
                    is_verified=True,
                ),
            ]
            db.session.add(product)
            product_index += 1

    for item in BANNERS:
        banner = Banner(
            position="hero",
            image=item["image"],
            link="/shop",
            is_active=True,
            sort_order=item["sort"],
            start_date=datetime.utcnow() - timedelta(days=1),
            end_date=datetime.utcnow() + timedelta(days=365),
        )
        banner.translations = [
            BannerTranslation(
                locale=locale,
                title=banner_texts(item, locale)[0],
                subtitle=banner_texts(item, locale)[1],
                button_text=banner_texts(item, locale)[2],
            )
            for locale in BANNER_LOCALES
        ]
        db.session.add(banner)

    db.session.commit()
