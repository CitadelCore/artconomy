<template>
  <v-dialog
      v-model="toggle"
      fullscreen
      ref="dialog"
      transition="dialog-bottom-transition"
      :overlay="false"
      scrollable
  >
    <v-card tile class="markdown-help">
      <v-toolbar flat dark color="primary">
        <v-btn icon @click.native="toggle = false" dark id="close-markdown-help">
          <v-icon>close</v-icon>
        </v-btn>
        <v-toolbar-title>Formatting Help</v-toolbar-title>
        <v-spacer/>
        <v-toolbar-items>
          <v-btn dark text @click.prevent="toggle=false">Close</v-btn>
        </v-toolbar-items>
      </v-toolbar>
      <v-card-text>
        <v-container fluid class="py-0">
        <v-row no-gutters   v-if="display" class="markdown-rendered-help">
          <v-col class="text-center" cols="12" >
            <h1>Artconomy uses Markdown!</h1>
            <p>Markdown is a language for enhancing your posts with links, lists, and other goodies. Here are some
              examples!</p>
          </v-col>
          <v-col cols="12" md="6" lg="5" offset-lg="1">
            <v-row no-gutters  >
              <v-col cols="12">
                <span class="title">Basics</span>
                <v-divider></v-divider>
              </v-col>
              <v-col cols="6"><v-subheader class="markdown-table-header">Write</v-subheader></v-col>
              <v-col cols="6"><v-subheader class="markdown-table-header">...and get</v-subheader></v-col>
              <template v-for="(item, index) in basicsItems">
                <v-col cols="12" :key="index">
                  <v-row no-gutters  >
                    <v-col cols="12" class="py-0"><v-divider></v-divider></v-col>
                    <v-col cols="6"><kbd>{{item.input}}</kbd></v-col>
                    <v-col cols="6" v-html="mdRenderInline(item.input)"></v-col>
                  </v-row>
                </v-col>
              </template>
            </v-row>
          </v-col>
          <v-col cols="12" md="6" lg="5">
            <v-row no-gutters  >
              <v-col cols="12">
                <span class="title">Links</span>
                <v-divider></v-divider>
              </v-col>
              <v-col cols="7" md="8" lg="7"><v-subheader class="markdown-table-header">Write</v-subheader></v-col>
              <v-col cols="5" md="4" lg="5"><v-subheader class="markdown-table-header">...and get</v-subheader></v-col>
              <template v-for="(item, index) in linksItems">
                <v-col cols="12" :key="index">
                  <v-row no-gutters  >
                    <v-col cols="12" class="py-0"><v-divider></v-divider></v-col>
                    <v-col cols="7" md="8" lg="7"><kbd>{{item.input}}</kbd></v-col>
                    <v-col cols="5" md="4" lg="5" v-html="mdRenderInline(item.input)"></v-col>
                  </v-row>
                </v-col>
              </template>
            </v-row>
          </v-col>
          <v-col class="hide-sm-and-down" cols="12" >
            <v-divider></v-divider>
          </v-col>
          <v-col cols="12" md="6" lg="5" offset-lg="1">
            <v-row no-gutters  >
              <v-col cols="12">
                <span class="title">Blocks</span>
                <v-divider></v-divider>
              </v-col>
              <v-col cols="12">
                <p>You can create paragraphs and other 'blocks' of text. Paragraphs should be separated by two newlines.
                  <strong>One new line is not enough!</strong>
                </p>
              </v-col>
              <v-col cols="6"><v-subheader class="markdown-table-header">Write</v-subheader></v-col>
              <v-col cols="6"><v-subheader class="markdown-table-header">...and get</v-subheader></v-col>
              <template v-for="(item, index) in blocksItems">
                <v-col cols="12" :key="index">
                  <v-row no-gutters  >
                    <v-col cols="12" class="py-0"><v-divider></v-divider></v-col>
                    <v-col cols="6"><kbd>{{item.input}}</kbd></v-col>
                    <v-col cols="6" v-html="mdRender(item.input)"></v-col>
                  </v-row>
                </v-col>
              </template>
            </v-row>
          </v-col>
          <v-col cols="12" md="6" lg="4" offset-lg="1">
            <v-row no-gutters  >
              <v-col cols="12">
                <span class="title">Lists</span>
                <v-divider></v-divider>
              </v-col>
              <v-col cols="12">
                <p>You can create numbered and bullet lists. <strong>You don't need to track the numbers yourself!</strong></p>
                <p>You can also nest paragraphs and other lists by indenting four spaces for each level.</p>
              </v-col>
              <v-col cols="7" md="8" lg="7"><v-subheader class="markdown-table-header">Write</v-subheader></v-col>
              <v-col cols="5" md="4" lg="5"><v-subheader class="markdown-table-header">...and get</v-subheader></v-col>
              <template v-for="(item, index) in listsItems">
                <v-col cols="12" :key="index">
                  <v-row no-gutters  >
                    <v-col cols="12" class="py-0"><v-divider></v-divider></v-col>
                    <v-col cols="7" md="8" lg="7"><kbd>{{item.input}}</kbd></v-col>
                    <v-col cols="5" md="4" lg="5" v-html="mdRender(item.input)"></v-col>
                  </v-row>
                </v-col>
              </template>
            </v-row>
          </v-col>
          <v-col cols="12" md="5" offset-lg="1">
            <v-row no-gutters  >
              <v-col cols="12">
                <span class="title">Headers</span>
                <v-divider></v-divider>
              </v-col>
              <v-col cols="12">
                <p>You can add headers to your post. Please use these sparingly.
                  <strong>You must start a header at the beginning of a line for this to work.</strong></p>
              </v-col>
              <v-col cols="7" md="8" lg="7"><v-subheader class="markdown-table-header">Write</v-subheader></v-col>
              <v-col cols="5" md="4" lg="5"><v-subheader class="markdown-table-header">...and get</v-subheader></v-col>
              <template v-for="(item, index) in headersItems">
                <v-col cols="12" :key="index">
                  <v-row no-gutters  >
                    <v-col cols="12" class="py-0"><v-divider></v-divider></v-col>
                    <v-col cols="7" md="8" lg="7"><kbd>{{item.input}}</kbd></v-col>
                    <v-col cols="5" md="4" lg="5" v-html="mdRender(item.input)"></v-col>
                  </v-row>
                </v-col>
              </template>
            </v-row>
          </v-col>
          <v-col cols="12" md="5">
            <v-row no-gutters  >
              <v-col cols="12">
                <span class="title">Extras</span>
                <v-divider></v-divider>
              </v-col>
              <v-col cols="12">
                <p>Here are a few extra tricks you might find handy!</p>
              </v-col>
              <v-col cols="7" md="8" lg="7"><v-subheader class="markdown-table-header">Write</v-subheader></v-col>
              <v-col cols="5" md="4" lg="5"><v-subheader class="markdown-table-header">...and get</v-subheader></v-col>
              <template v-for="(item, index) in extrasItems">
                <v-col cols="12" :key="index">
                  <v-row no-gutters  >
                    <v-col cols="12" class="py-0"><v-divider></v-divider></v-col>
                    <v-col cols="7" md="8" lg="7"><kbd>{{item.input}}</kbd></v-col>
                    <v-col cols="5" md="4" lg="5" v-html="mdRender(item.input)"></v-col>
                  </v-row>
                </v-col>
              </template>
            </v-row>
          </v-col>
          <v-col cols="12" class="hidden-xs-only text-center mt-4">
            <v-btn color="primary" @click.prevent="toggle = false">Back</v-btn>
          </v-col>
        </v-row>
        </v-container>
      </v-card-text>
    </v-card>
  </v-dialog>
</template>

<style lang="sass">
  .markdown-help
    .markdown-table-header
      height: unset
      padding: 0 !important
    kbd
      &::before, &::after
        content: unset
    table.v-datatable.v-table
      tbody tr td
        padding: 0 10px
      thead tr th
        padding: 0 10px
</style>

<script lang="ts">
import Component, {mixins} from 'vue-class-component'
import {Prop} from 'vue-property-decorator'
import Formatting from '@/mixins/formatting'

  @Component
export default class AcMarkdownExplination extends mixins(Formatting) {
    @Prop({required: true})
    public value!: boolean

    public display = false
    public headers = [
      {
        text: 'Write...',
        sortable: false,
        value: 'input',
      },
      {
        text: 'and get',
        sortable: false,
        value: 'input',
      },
    ]

    public basicsItems = [
      {input: '*Emphasis*'},
      {input: '_Also Emphasis_'},
      {input: '**Strong**'},
      {input: '__Also Strong__'},
      {input: '**Strong and then _Emphasized_**'},
      {input: '___Strong and Emphasized___'},
      {input: '~~Deleted~~'},
      {input: '`code`'},
    ]

    public linksItems = [
      {input: 'https://artconomy.com/'},
      {input: '[A link](https://artconomy.com/)'},
      {input: 'contact@artconomy.com'},
      {input: '[Email us](mailto:contact@artconomy.com)'},
    ]

    public blocksItems = [
      {input: 'This is a test.\nThis is only a test.'},
      {input: 'This is a test.\n\nThis is only a test.'},
      {input: '> This is a block quote.\nIt continues on the next line.\n\nYou need two lines to stop here, too!'},
      {input: '> This is another block quote.\n> \n> We can add blank lines to quotes this way.'},
      {input: '```\n# This is a code block.\n\nfunction greet():\n    print("Hello, world!")\n\ngreet()\n```'},
    ]

    public listsItems = [
      {input: '1. Put on shoes\n1. Tie laces\n1. Grab keys\n1. Forget wallet'},
      {input: '* Fox\n* Wolf\n* Human\n* Elf'},
      {input: '- Fox\n+ Wolf\n+ Human\n- Elf'},
      {
        input: '1. First item\n    * Sub item\n    * Sub item 2\n2. Second item\n\n    ' +
              'This is a test paragraph.\n\n1. Third item',
      },
    ]

    public headersItems = [
      {input: '# Header 1'},
      {input: 'Header 1\n==='},
      {input: '## Header 2'},
      {input: 'Header 2\n---'},
      {input: '### Header 3'},
      {input: '#### Header 4'},
      {input: '##### Header 5'},
      {input: '###### Header 6'},
    ]

    public extrasItems = [
      {
        input: '**Tables**\n\n' +
              '| Headers       | Go            | Here  |\n' +
              '| ------------- |:-------------:| -----:|\n' +
              '| col 3 is      | right-aligned |  $600 |\n' +
              '| col 2 is      | centered      |   $12 |\n' +
              '| zebra stripes | are neat      |    $1 |\n',
      },
      {input: '**Images**\n\n![Artconomy Logo](https://artconomy.com/static/images/logo.png)'},
      {
        input: '**Dividers**\n\nWe thought driving downtown wouldn\'t take that long.\n\n***\n\nThree hours later...' +
              '\n\n---\n\n"Why did we do this again?"',
      },
    ]

    public get toggle() {
      if (this.value) {
        // Lazy evaluation with caching of all the Markdown examples.
        this.display = true
      }
      return this.value
    }

    public set toggle(val: boolean) {
      this.$emit('input', val)
    }
}
</script>
