/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component, onWillStart, useState } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { user } from "@web/core/user";
import { browser } from "@web/core/browser/browser";

/**
 * Systray button that toggles the current user's UI language between English
 * and Arabic, then reloads. Kept deliberately tiny and dependency-free so it
 * survives Odoo upgrades better than a third-party module.
 */
export class LanguageSwitch extends Component {
    static template = "connect_pack.LanguageSwitch";
    static props = {};

    setup() {
        this.orm = useService("orm");
        this.state = useState({ arCode: "ar_001" });
        onWillStart(async () => {
            const langs = await this.orm.searchRead(
                "res.lang",
                [
                    ["active", "=", true],
                    ["code", "=like", "ar%"],
                ],
                ["code"],
                { limit: 1 }
            );
            if (langs.length) {
                this.state.arCode = langs[0].code;
            }
        });
    }

    get isArabic() {
        return (user.lang || "en_US").startsWith("ar");
    }

    get buttonLabel() {
        return this.isArabic ? "EN" : "ع";
    }

    get buttonTitle() {
        return this.isArabic ? "Switch to English" : "التبديل إلى العربية";
    }

    async onToggle() {
        const target = this.isArabic ? "en_US" : this.state.arCode;
        await this.orm.write("res.users", [user.userId], { lang: target });
        browser.location.reload();
    }
}

registry.category("systray").add(
    "connect_pack.LanguageSwitch",
    { Component: LanguageSwitch },
    { sequence: 100 }
);
