<%!

def f_iftrue(exp, val):
    if exp:
        return val
    return ''
    
def f_iffalse(exp, val):
    if not exp:
        return val
    return ''    

def test(echo):
    return echo

%>


<%def name="iftrue(exp, value)">${f_iftrue(exp, value)}</%def>

<%def name="iffalse(exp, value)">${f_iffalse(exp, value)}</%def>

<%def name="ifchecked(exp=None)">${f_iftrue(exp, 'checked="checked"')}</%def>

<%def name="ifselected(exp=None)">${f_iftrue(exp, 'selected="selected"')}</%def>


<%def name="text(name, value=None, required=False, cls='')">
    <%
        if value is None: value = ''
    %>
    % if required:
        <input name="${name}" value="${value}" class="${cls}" required="required" />
    % else:
        <input name="${name}" value="${value}" class="${cls}" />    
    % endif
</%def>



<%def name="textarea(name, value=None, required=False, cls='')">
    <%
        if value is None: value = ''
    %>
    % if required:
        <textarea name="${name}" class="${cls}" required="required" />${value}</textarea>
    % else:
        <textarea name="${name}" class="${cls}" />${value}</textarea>
    % endif
</%def>




<%def name="checkbox(name, v, label=None, value=None, required=False, cls='')">
    <%
    if required:
        required = 'required="required"'
    else:
        required = ""        
    %>
    % if v == value:
        <input type="checkbox" name="${name}" ${required} checked="checked" id="checkbox_${name}">
    % else:
        <input type="checkbox" name="${name}" ${required} id="checkbox_${name}">    
    % endif
    <label for="">${label or v}</label>
</%def>



<%def name="checkboxes(name, v, values=None, required=False, cls='', elem=None)">
    <%
    values = values or []
    if hasattr(v, "items"):
        v = v.items()
    else:
        v = [[i,i] for i in v]

    if required:
        required = 'required="required"'
    else:
        required = ""
    %>
    % for count, (i,j) in enumerate(v):
        % if elem:
            <${elem}>
        % endif
            % if i in values:
                <input type="checkbox" name="${name}" class="${cls}" ${required} checked="checked" id="checkbox_${name}_${count}" value="${i}" /> 
                <label for="checkbox_${name}_${count}">${j}</label>
            % else:
                <input type="checkbox" name="${name}" class="${cls}" ${required} id="checkbox_${name}_${count}" value="${i}" /> 
                <label for="checkbox_${name}_${count}">${j}</label>
            % endif
        
        % if elem:
            </${elem}>
        % endif
    % endfor

</%def>



<%def name="radios(name, v, value=None, required=False, cls='', elem=None)">
    <%

    if hasattr(v, "items"):
        v = v.items()
    else:
        v = [[i,i] for i in v]

    if required:
        required = 'required="required"'
    else:
        required = ""
    %>
    % for count, (i,j) in enumerate(v):
        % if elem:
            <${elem}>
        % endif
            % if i == value:
                <input type="radio" name="${name}" class="${cls}" ${required} checked="checked" id="radio_${name}_${count}" value="${i}" /> 
                <label for="radio_${name}_${count}">${j}</label>
            % else:
                <input type="radio" name="${name}" class="${cls}" ${required} id="radio_${name}_${count}" value="${i}"/> 
                <label for="radio_${name}_${count}">${j}</label>
            % endif
            
        % if elem:
            </${elem}>
        % endif
    % endfor
</%def>




<%def name="select(name, v, value=None, required=False, cls='')">
    <% 
    if hasattr(v, "items"):
        v = v.items()
    else:
        v = [[i,i] for i in v]
    %>
    
    % if required:
        <select name="${name}" required="required" class="${cls}">
    % else:
        <select name="${name}" class="${cls}"> 
    % endif

        <option></option>
        % for i,j in v:
            % if i == value:
                <option selected="selected" value="${i}">${j}</option>
            % else:
                <option value="${i}">${j}</option>
            % endif
        % endfor
    </select>
</%def>




<%def name="countries()">
    <option value=""></option>
    <option value="Afghanistan">Afghanistan</option>
    <option value="Albania">Albania</option>
    <option value="Algeria">Algeria</option>
    <option value="American Samoa">American Samoa</option>
    <option value="Andorra">Andorra</option>
    <option value="Angola">Angola</option>
    <option value="Anguilla">Anguilla</option>
    <option value="Antarctica">Antarctica</option>
    <option value="Antigua And Barbuda">Antigua And Barbuda</option>
    <option value="Argentina">Argentina</option>
    <option value="Armenia">Armenia</option>
    <option value="Aruba">Aruba</option>
    <option value="Australia">Australia</option>
    <option value="Austria">Austria</option>
    <option value="Azerbaijan">Azerbaijan</option>
    <option value="Bahamas">Bahamas</option>
    <option value="Bahrain">Bahrain</option>
    <option value="Bangladesh">Bangladesh</option>
    <option value="Barbados">Barbados</option>
    <option value="Belarus">Belarus</option>
    <option value="Belgium">Belgium</option>
    <option value="Belize">Belize</option>
    <option value="Benin">Benin</option>
    <option value="Bermuda">Bermuda</option>
    <option value="Bhutan">Bhutan</option>
    <option value="Bolivia, Plurinational State Of">Bolivia, Plurinational State Of</option>
    <option value="Bosnia And Herzegovina">Bosnia And Herzegovina</option>
    <option value="Botswana">Botswana</option>
    <option value="Bouvet Island">Bouvet Island</option>
    <option value="Brazil">Brazil</option>
    <option value="British Indian Ocean Territory">British Indian Ocean Territory</option>
    <option value="Brunei Darussalam">Brunei Darussalam</option>
    <option value="Bulgaria">Bulgaria</option>
    <option value="Burkina Faso">Burkina Faso</option>
    <option value="Burundi">Burundi</option>
    <option value="Cambodia">Cambodia</option>
    <option value="Cameroon">Cameroon</option>
    <option value="Canada">Canada</option>
    <option value="Cape Verde">Cape Verde</option>
    <option value="Cayman Islands">Cayman Islands</option>
    <option value="Central African Republic">Central African Republic</option>
    <option value="Chad">Chad</option>
    <option value="Chile">Chile</option>
    <option value="China">China</option>
    <option value="Christmas Island">Christmas Island</option>
    <option value="Cocos (Keeling) Islands">Cocos (Keeling) Islands</option>
    <option value="Colombia">Colombia</option>
    <option value="Comoros">Comoros</option>
    <option value="Congo">Congo</option>
    <option value="Congo, The Democratic Republic Of The">Congo, The Democratic Republic Of The</option>
    <option value="Cook Islands">Cook Islands</option>
    <option value="Costa Rica">Costa Rica</option>
    <option value="Côte D'Ivoire">Côte D'Ivoire</option>
    <option value="Croatia">Croatia</option>
    <option value="Cuba">Cuba</option>
    <option value="Cyprus">Cyprus</option>
    <option value="Czech Republic">Czech Republic</option>
    <option value="Denmark">Denmark</option>
    <option value="Djibouti">Djibouti</option>
    <option value="Dominica">Dominica</option>
    <option value="Dominican Republic">Dominican Republic</option>
    <option value="Ecuador">Ecuador</option>
    <option value="Egypt">Egypt</option>
    <option value="El Salvador">El Salvador</option>
    <option value="Equatorial Guinea">Equatorial Guinea</option>
    <option value="Eritrea">Eritrea</option>
    <option value="Estonia">Estonia</option>
    <option value="Ethiopia">Ethiopia</option>
    <option value="Falkland Islands (Malvinas)">Falkland Islands (Malvinas)</option>
    <option value="Faroe Islands">Faroe Islands</option>
    <option value="Fiji">Fiji</option>
    <option value="Finland">Finland</option>
    <option value="France">France</option>
    <option value="French Guiana">French Guiana</option>
    <option value="French Polynesia">French Polynesia</option>
    <option value="French Southern Territories">French Southern Territories</option>
    <option value="Gabon">Gabon</option>
    <option value="Gambia">Gambia</option>
    <option value="Georgia">Georgia</option>
    <option value="Germany">Germany</option>
    <option value="Ghana">Ghana</option>
    <option value="Gibraltar">Gibraltar</option>
    <option value="Greece">Greece</option>
    <option value="Greenland">Greenland</option>
    <option value="Grenada">Grenada</option>
    <option value="Guadeloupe">Guadeloupe</option>
    <option value="Guam">Guam</option>
    <option value="Guatemala">Guatemala</option>
    <option value="Guernsey">Guernsey</option>
    <option value="Guinea">Guinea</option>
    <option value="Guinea-Bissau">Guinea-Bissau</option>
    <option value="Guyana">Guyana</option>
    <option value="Haiti">Haiti</option>
    <option value="Heard Island And Mcdonald Islands">Heard Island And Mcdonald Islands</option>
    <option value="Honduras">Honduras</option>
    <option value="Hong Kong">Hong Kong</option>
    <option value="Hungary">Hungary</option>
    <option value="Iceland">Iceland</option>
    <option value="India">India</option>
    <option value="Indonesia">Indonesia</option>
    <option value="Iran, Islamic Republic Of">Iran, Islamic Republic Of</option>
    <option value="Iraq">Iraq</option>
    <option value="Ireland">Ireland</option>
    <option value="Isle Of Man">Isle Of Man</option>
    <option value="Israel">Israel</option>
    <option value="Italy">Italy</option>
    <option value="Jamaica">Jamaica</option>
    <option value="Japan">Japan</option>
    <option value="Jersey">Jersey</option>
    <option value="Jordan">Jordan</option>
    <option value="Kazakhstan">Kazakhstan</option>
    <option value="Kenya">Kenya</option>
    <option value="Kiribati">Kiribati</option>
    <option value="Korea, Democratic People's Republic Of">Korea, Democratic People's Republic Of</option>
    <option value="Korea, Republic Of">Korea, Republic Of</option>
    <option value="Kuwait">Kuwait</option>
    <option value="Kyrgyzstan">Kyrgyzstan</option>
    <option value="Lao People's Democratic Republic">Lao People's Democratic Republic</option>
    <option value="Latvia">Latvia</option>
    <option value="Lebanon">Lebanon</option>
    <option value="Lesotho">Lesotho</option>
    <option value="Liberia">Liberia</option>
    <option value="Libyan Arab Jamahiriya">Libyan Arab Jamahiriya</option>
    <option value="Liechtenstein">Liechtenstein</option>
    <option value="Lithuania">Lithuania</option>
    <option value="Luxembourg">Luxembourg</option>
    <option value="Macao">Macao</option>
    <option value="Macedonia, The Former Yugoslav Republic Of">Macedonia, The Former Yugoslav Republic Of</option>
    <option value="Madagascar">Madagascar</option>
    <option value="Malawi">Malawi</option>
    <option value="Malaysia">Malaysia</option>
    <option value="Maldives">Maldives</option>
    <option value="Mali">Mali</option>
    <option value="Malta">Malta</option>
    <option value="Marshall Islands">Marshall Islands</option>
    <option value="Martinique">Martinique</option>
    <option value="Mauritania">Mauritania</option>
    <option value="Mauritius">Mauritius</option>
    <option value="Mayotte">Mayotte</option>
    <option value="Mexico">Mexico</option>
    <option value="Micronesia, Federated States Of">Micronesia, Federated States Of</option>
    <option value="Moldova, Republic Of">Moldova, Republic Of</option>
    <option value="Monaco">Monaco</option>
    <option value="Mongolia">Mongolia</option>
    <option value="Montenegro">Montenegro</option>
    <option value="Montserrat">Montserrat</option>
    <option value="Morocco">Morocco</option>
    <option value="Mozambique">Mozambique</option>
    <option value="Myanmar">Myanmar</option>
    <option value="Namibia">Namibia</option>
    <option value="Nauru">Nauru</option>
    <option value="Nepal">Nepal</option>
    <option value="Netherlands">Netherlands</option>
    <option value="Netherlands Antilles">Netherlands Antilles</option>
    <option value="New Caledonia">New Caledonia</option>
    <option value="New Zealand">New Zealand</option>
    <option value="Nicaragua">Nicaragua</option>
    <option value="Niger">Niger</option>
    <option value="Nigeria">Nigeria</option>
    <option value="Niue">Niue</option>
    <option value="Norfolk Island">Norfolk Island</option>
    <option value="Northern Mariana Islands">Northern Mariana Islands</option>
    <option value="Norway">Norway</option>
    <option value="Oman">Oman</option>
    <option value="Pakistan">Pakistan</option>
    <option value="Palau">Palau</option>
    <option value="Palestinian Territory, Occupied">Palestinian Territory, Occupied</option>
    <option value="Panama">Panama</option>
    <option value="Papua New Guinea">Papua New Guinea</option>
    <option value="Paraguay">Paraguay</option>
    <option value="Peru">Peru</option>
    <option value="Philippines">Philippines</option>
    <option value="Pitcairn">Pitcairn</option>
    <option value="Poland">Poland</option>
    <option value="Portugal">Portugal</option>
    <option value="Puerto Rico">Puerto Rico</option>
    <option value="Qatar">Qatar</option>
    <option value="Réunion">Réunion</option>
    <option value="Romania">Romania</option>
    <option value="Russian Federation">Russian Federation</option>
    <option value="Rwanda">Rwanda</option>
    <option value="Saint Barthélemy">Saint Barthélemy</option>
    <option value="Saint Helena, Ascension And Tristan Da Cunha">Saint Helena, Ascension And Tristan Da Cunha</option>
    <option value="Saint Kitts And Nevis">Saint Kitts And Nevis</option>
    <option value="Saint Lucia">Saint Lucia</option>
    <option value="Saint Martin">Saint Martin</option>
    <option value="Saint Pierre And Miquelon">Saint Pierre And Miquelon</option>
    <option value="Saint Vincent And The Grenadines">Saint Vincent And The Grenadines</option>
    <option value="Samoa">Samoa</option>
    <option value="San Marino">San Marino</option>
    <option value="Sao Tome And Principe">Sao Tome And Principe</option>
    <option value="Saudi Arabia">Saudi Arabia</option>
    <option value="Senegal">Senegal</option>
    <option value="Serbia">Serbia</option>
    <option value="Seychelles">Seychelles</option>
    <option value="Sierra Leone">Sierra Leone</option>
    <option value="Singapore">Singapore</option>
    <option value="Slovakia">Slovakia</option>
    <option value="Slovenia">Slovenia</option>
    <option value="Solomon Islands">Solomon Islands</option>
    <option value="Somalia">Somalia</option>
    <option value="South Africa">South Africa</option>
    <option value="South Georgia And The South Sandwich Islands">South Georgia And The South Sandwich Islands</option>
    <option value="Spain">Spain</option>
    <option value="Sri Lanka">Sri Lanka</option>
    <option value="Sudan">Sudan</option>
    <option value="Suriname">Suriname</option>
    <option value="Svalbard And Jan Mayen">Svalbard And Jan Mayen</option>
    <option value="Swaziland">Swaziland</option>
    <option value="Sweden">Sweden</option>
    <option value="Switzerland">Switzerland</option>
    <option value="Syrian Arab Republic">Syrian Arab Republic</option>
    <option value="Taiwan, Province Of China">Taiwan, Province Of China</option>
    <option value="Tajikistan">Tajikistan</option>
    <option value="Tanzania, United Republic Of">Tanzania, United Republic Of</option>
    <option value="Thailand">Thailand</option>
    <option value="Timor-Leste">Timor-Leste</option>
    <option value="Togo">Togo</option>
    <option value="Tokelau">Tokelau</option>
    <option value="Tonga">Tonga</option>
    <option value="Trinidad And Tobago">Trinidad And Tobago</option>
    <option value="Tunisia">Tunisia</option>
    <option value="Turkey">Turkey</option>
    <option value="Turkmenistan">Turkmenistan</option>
    <option value="Turks And Caicos Islands">Turks And Caicos Islands</option>
    <option value="Tuvalu">Tuvalu</option>
    <option value="Uganda">Uganda</option>
    <option value="Ukraine">Ukraine</option>
    <option value="United Arab Emirates">United Arab Emirates</option>
    <option value="United Kingdom">United Kingdom</option>
    <option value="United States" selected="selected">United States</option>
    <option value="United States Minor Outlying Islands">United States Minor Outlying Islands</option>
    <option value="Uruguay">Uruguay</option>
    <option value="Uzbekistan">Uzbekistan</option>
    <option value="Vanuatu">Vanuatu</option>
    <option value="Vatican City State">Vatican City State</option>
    <option value="Venezuela, Bolivarian Republic Of">Venezuela, Bolivarian Republic Of</option>
    <option value="Viet Nam">Viet Nam</option>
    <option value="Virgin Islands, British">Virgin Islands, British</option>
    <option value="Virgin Islands, U.S.">Virgin Islands, U.S.</option>
    <option value="Wallis And Futuna">Wallis And Futuna</option>
    <option value="Western Sahara">Western Sahara</option>
    <option value="Yemen">Yemen</option>
    <option value="Zambia">Zambia</option>
    <option value="Zimbabwe">Zimbabwe</option>
    <option value="Åland Islands">Åland Islands</option>
</%def>