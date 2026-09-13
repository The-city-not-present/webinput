

projectspecific_css = '''


.page-webinput h1 {
    color: #555;
    font-size: 16px;
    margin-top: 15px;
}


.webinput-controls-thumb.mdmreport-banner {
    padding: 0;
    border: none;
}
.webinput-controls-thumb.mdmreport-banner.webinput-controls-type-compound {
    padding: 14px;
    border: 1px solid #e2e2e2;
}

.webinput .mdmreport-controls .mdmreport-control {
    display: inline-block;
}
.webinput .mdmreport-controls label {
    padding: 0
}

.form-controls input, .mdmreport-control, .webinput-control-submit {
    min-width: 215px;
}

.webinput-control-submit {
    padding: 6px 26px 6px;
    color: #111;
    font-weight: 500;
    /*border: 3px solid transparent; */
    background: #fff;
    border: 4px solid #4a3;
    cursor: pointer;
}
.webinput-control-submit:hover {
    color: #000;
    border-color: #261;
    background: #261;
    color: #fff;
}




.webinput-control-singlepunch-category-container {
    display: block;
    position: relative;
    border: none;
    padding: 0;
    margin-bottom: 7px;
}
.webinput-control-singlepunch-category-container input, .webinput-control-singlepunch-category-container input.mdmreport-control, .webinput .webinput-control-singlepunch-category-container input.mdmreport-control {
    display: none;
}
.webinput-control-singlepunch-category-container label, .webinput .webinput-control-singlepunch-category-container label, .webinput .mdmreport-controls .webinput-control-singlepunch-category-container label {
    display: block;
    position: relative;
    border-radius: 4px;
    border: 3px solid transparent;
    padding: 5px 12px 5px;
    margin-bottom: 7px;
    cursor: pointer;
    transition: all 300ms ease;
    /* box-shadow: inset 0 0 3px 1px rgba(192,192,192,.3); */
    outline: 1px solid #ddd;
    outline-offset: -1px;
}
.webinput-control-singlepunch-category-container label:hover, .webinput .webinput-control-singlepunch-category-container label:hover, .webinput .mdmreport-controls .webinput-control-singlepunch-category-container label:hover {
    border-color: #ddd;
    padding: 5px 12px 5px;
    border-width: 3px;
    outline: 1px solid #ddd;
    outline-offset: -1px;
}
.webinput-control-singlepunch-category-container input:checked + label, .webinput-control-singlepunch-category-container input.mdmreport-control:checked + label, .webinput .webinput-control-singlepunch-category-container input.mdmreport-control:checked + label {
    border-color: #666;
    padding: 5px 12px 5px;
    border-width: 3px;
    outline: 1px solid transparent;
    outline-offset: -1px;
}

'''