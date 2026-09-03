/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component, onWillStart, useState } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { user } from "@web/core/user";

/**
 * Systray button that toggles the current user's UI language between English
 * and Arabic. It always re-reads the *current* language from the server before
 * deciding the target, so it can never get stuck out of sync with a stale
 * client-side value.
 */
export class LanguageSwitch extends Component {
    static template = "connect_pack.LanguageSwitch";
    static props = {};

    setup() {
        this.orm = useService("orm");
        this.action = useService("action");
        this.state = useState({ lang: user.lang || "en_US", arCode: "ar_001" });

        onWillStart(async () => {
            const [langs, [me]] = await Promise.all([
                this.orm.searchRead(
                    "res.lang",
                    [["active", "=", true], ["code", "=like", "ar%"]],
                    ["code"],
                    { limit: 1 },
                ),
                this.orm.read("res.users", [user.userId], ["lang"]),
            ]);
            if (langs.length) {
                this.state.arCode = langs[0].code;
            }
            if (me) {
                this.state.lang = me.lang || "en_US";
            }
        });
    }

    get isArabic() {
        return (this.state.lang || "").startsWith("ar");
    }

    get buttonLabel() {
        return this.isArabic ? "EN" : "ع";
    }

    get buttonTitle() {
        return this.isArabic ? "Switch to English" : "التبديل إلى العربية";
    }

    async onToggle() {
        const [me] = await this.orm.read("res.users", [user.userId], ["lang"]);
        const current = (me && me.lang) || "en_US";
        const target = current.startsWith("ar") ? "en_US" : this.state.arCode;
        await this.orm.write("res.users", [user.userId], { lang: target });
        await this.action.doAction("reload_context");
    }
}

registry.category("systray").add(
    "connect_pack.LanguageSwitch",
    { Component: LanguageSwitch },
    { sequence: 100 },
);
