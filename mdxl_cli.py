<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE language SYSTEM "language.dtd">
<language name="Markdown XL" version="3" kateversion="5.0" section="Markup" extensions="*.mdxl" mimetype="text/x-mdxl" author="AI" license="MIT">
    <highlighting>
        <list name="mdxl_completions">
            <item>-# </item> <item>-## </item> <item>-### </item> <item>#### </item>
            <item>`````python</item> <item>`````bash</item>
            <item>/!!!/</item> <item>/col//</item> <item>/col#</item>
            <item>||||[</item> <item>]||||</item>
            <item>[[==>>]]</item> <item>[[<<==]]</item> <item>[[<=>>]]</item> <item>>> </item>
        </list>

        <contexts>
            <context attribute="Normal Text" lineBeginContext="#stay" lineEndContext="#stay" name="Normal Text">
                <!-- Micro Headers -->
                <RegExpr attribute="MicroHeader1" context="#stay" String="^-#\s.*$" column="0"/>
                <RegExpr attribute="MicroHeader2" context="#stay" String="^-##\s.*$" column="0"/>
                <RegExpr attribute="MicroHeader3" context="#stay" String="^-###\s.*$" column="0"/>
                <RegExpr attribute="SubHeader" context="#stay" String="^####\s.*$" column="0"/>
                <RegExpr attribute="Header" context="#stay" String="^#{1,6}\s.*$" column="0"/>
                
                <!-- Executable Code Blocks -->
                <RegExpr attribute="CodeBlock" context="CodeBlock" String="^`````.*$" beginRegion="Code"/>
                
                <!-- Standard Markdown -->
                <Detect2Chars attribute="Bold" context="Bold" char="*" char1="*"/>
                <DetectChar attribute="Italic" context="Italic" char="*"/>
                <DetectChar attribute="CodeInline" context="CodeInline" char="`"/>
                
                <!-- MDXL Specials -->
                <StringDetect attribute="Special" context="UpsideDown" String="/!!!/"/>
                <StringDetect attribute="Blockquote" context="#stay" String=">>"/>
                <StringDetect attribute="Arrow" context="#stay" String="[[==>"/>
                <StringDetect attribute="Arrow" context="#stay" String="[[&lt;&lt;=="/>
                <StringDetect attribute="Arrow" context="#stay" String="[[&lt;=&gt;"/>
                
                <!-- Native Invisible Ink (Black text on Black background) -->
                <RegExpr attribute="InvisibleInk" context="#stay" String="\|\|\|\|\[.*?\]\|\|\|\|"/>
                
                <!-- Colors -->
                <StringDetect attribute="ColorTag" context="ColorText" String="/col//"/>
            </context>
            
            <context attribute="Bold" lineBeginContext="#stay" lineEndContext="#stay" name="Bold"><Detect2Chars attribute="Bold" context="#pop" char="*" char1="*"/></context>
            <context attribute="Italic" lineBeginContext="#stay" lineEndContext="#stay" name="Italic"><DetectChar attribute="Italic" context="#pop" char="*"/></context>
            <context attribute="CodeInline" lineBeginContext="#stay" lineEndContext="#stay" name="CodeInline"><DetectChar attribute="CodeInline" context="#pop" char="`"/></context>
            <context attribute="CodeBlock" lineBeginContext="#stay" lineEndContext="#stay" name="CodeBlock"><RegExpr attribute="CodeBlock" context="#pop" String="^``````*$" endRegion="Code"/></context>
            <context attribute="UpsideDown" lineBeginContext="#stay" lineEndContext="#stay" name="UpsideDown"><StringDetect attribute="Special" context="#pop" String="/!!!/"/></context>
            <context attribute="ColorText" lineBeginContext="#stay" lineEndContext="#stay" name="ColorText"><RegExpr attribute="ColorTag" context="#pop" String="/col#[0-9a-fA-F]{6}//"/></context>
        </contexts>
        
        <itemDatas>
            <itemData name="Normal Text" defStyleNum="dsNormal"/>
            <itemData name="Header" defStyleNum="dsFunction" bold="1"/>
            <itemData name="MicroHeader1" defStyleNum="dsDataType" bold="1" color="#555555"/>
            <itemData name="MicroHeader2" defStyleNum="dsDataType" bold="1" color="#777777"/>
            <itemData name="MicroHeader3" defStyleNum="dsDataType" bold="1" color="#999999"/>
            <itemData name="SubHeader" defStyleNum="dsDataType" bold="1" color="#444444"/>
            <itemData name="Bold" defStyleNum="dsNormal" bold="1"/>
            <itemData name="Italic" defStyleNum="dsNormal" italic="1"/>
            <itemData name="CodeInline" defStyleNum="dsConstant" color="#d14"/>
            <itemData name="CodeBlock" defStyleNum="dsString"/>
            <itemData name="Special" defStyleNum="dsKeyword" color="#e36209"/>
            <itemData name="Blockquote" defStyleNum="dsComment" italic="1"/>
            <itemData name="Arrow" defStyleNum="dsDataType" bold="1" color="#007bff"/>
            <!-- Native Invisible Ink: foreground matches background -->
            <itemData name="InvisibleInk" defStyleNum="dsNormal" color="#333333" backgroundColor="#333333"/>
            <itemData name="ColorTag" defStyleNum="dsKeyword" color="#ff0000" bold="1"/>
            <itemData name="ColorText" defStyleNum="dsNormal" color="#ff00ff"/>
        </itemDatas>
        
        <completion>
            <item>-# </item> <item>-## </item> <item>-### </item> <item>#### </item>
            <item>`````python</item> <item>`````bash</item>
            <item>/!!!/</item> <item>/col//</item> <item>/col#</item>
            <item>||||[</item> <item>]||||</item>
            <item>[[==>>]]</item> <item>[[<<==]]</item> <item>[[<=>>]]</item> <item>>> </item>
        </completion>
    </highlighting>
</language>
